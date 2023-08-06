import collections
import math
from collections import OrderedDict
import numpy as np
import logging
from einops import rearrange

import torch
import torch.nn as nn
import torch.nn.functional as F

from tl2 import tl2_utils
from tl2.proj.pytorch import torch_utils
from tl2.proj.pytorch import init_func
from tl2.proj.pytorch.pytorch_hook import VerboseModel
from tl2.proj.fvcore import global_cfg


class Sine(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               w0=20.):
    super().__init__()

    self.repr_str = f"w0={w0}"

    self.w0 = w0
    pass

  def forward(self, x):
    return torch.sin(self.w0 * x)


class SirenLayer(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim,
               use_bias=True,
               w0=1.,
               is_first=False, # for initialization
               **kwargs):
    super().__init__()
    self.repr_str = f"input_dim={input_dim}, " \
                    f"hidden_dim={hidden_dim}, " \
                    f"use_bias={use_bias}, " \
                    f"w0={w0}, " \
                    f"is_first={is_first}"

    self.layer = nn.Linear(input_dim, hidden_dim, bias=use_bias)
    self.activation = Sine(w0)
    self.is_first = is_first
    self.input_dim = input_dim
    self.w0 = w0
    self.c = 6
    self.reset_parameters()
    pass

  def reset_parameters(self):
    with torch.no_grad():
      dim = self.input_dim
      w_std = (1 / dim) if self.is_first else (math.sqrt(self.c / dim) / self.w0)
      self.layer.weight.uniform_(-w_std, w_std)
      if self.layer.bias is not None:
        self.layer.bias.uniform_(-w_std, w_std)
    pass

  def forward(self, x):
    out = self.layer(x)
    out = self.activation(out)
    return out


class ModSirenLayer(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim,
               style_dim,
               w0=1.,
               is_first=False, # for initialization
               **kwargs):
    super().__init__()
    self.repr_str = f"input_dim={input_dim}, " \
                    f"hidden_dim={hidden_dim}, " \
                    f"style_dim={style_dim}, " \
                    f"w0={w0}, " \
                    f"is_first={is_first}"

    from . import cips_net
    # self.layer = nn.Linear(input_dim, hidden_dim, bias=use_bias)
    self.layer = cips_net.ModFC(in_channel=input_dim,
                                out_channel=hidden_dim,
                                style_dim=style_dim)

    self.activation = Sine(w0)
    self.is_first = is_first
    self.input_dim = input_dim
    self.w0 = w0
    self.c = 6
    self.reset_parameters()
    pass

  def reset_parameters(self):
    with torch.no_grad():
      dim = self.input_dim
      w_std = (1 / dim) if self.is_first else (math.sqrt(self.c / dim) / self.w0)
      self.layer.weight.uniform_(-w_std, w_std)
      # if self.layer.bias is not None:
      #   self.layer.bias.uniform_(-w_std, w_std)
    pass

  def forward(self,
              x,
              style):
    out = self.layer(x, style)
    out = self.activation(out)
    return out


class SkipLayer(nn.Module):
  def __init__(self, ):
    super(SkipLayer, self).__init__()

  def forward(self, x0, x1):
    # out = (x0 + x1) / math.pi
    out = (x0 + x1) / math.sqrt(2)
    return out


class ModSirenBlock(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               in_dim,
               out_dim,
               style_dim,
               name_prefix,
               **kwargs):
    super().__init__()

    self.repr_str = f"in_dim={in_dim}, " \
                    f"out_dim={out_dim}, " \
                    f"style_dim={style_dim})"

    self.in_dim = in_dim
    self.out_dim = out_dim
    self.style_dim = style_dim
    self.name_prefix = name_prefix

    self.style_dim_dict = {}

    self.mod1 = ModSirenLayer(input_dim=in_dim,
                              hidden_dim=out_dim,
                              style_dim=style_dim)
    self.style_dim_dict[f'{name_prefix}_0'] = style_dim

    self.mod2 = ModSirenLayer(input_dim=out_dim,
                              hidden_dim=out_dim,
                              style_dim=style_dim)
    self.style_dim_dict[f'{name_prefix}_1'] = style_dim

    self.skip = SkipLayer()
    pass

  def forward(self,
              x,
              style_dict,
              skip=True):
    """

    :param x: (b, in_c, h, w), (b, in_c), (b, n, in_c)
    :param style_dict:
    :param skip:
    :return:
    """
    x_orig = x

    style = style_dict[f'{self.name_prefix}_0']
    x = self.mod1(x, style)

    style = style_dict[f'{self.name_prefix}_1']
    x = self.mod2(x, style)

    out = x

    if skip and out.shape[-1] == x_orig.shape[-1]:
      # out = (out + x_orig) / 1.41421
      out = self.skip(out, x_orig)
    return out


class ToRGB(nn.Module):
  def __init__(self,
               in_dim,
               dim_rgb=3):
    super().__init__()
    self.in_dim = in_dim
    self.dim_rgb = dim_rgb

    self.linear = nn.Linear(in_dim, dim_rgb)
    pass

  def forward(self,
              input,
              skip=None):

    out = self.linear(input)

    if skip is not None:
      out = out + skip
    return out


def _frequency_init(freq):
  def init(m):
    with torch.no_grad():
      if isinstance(m, nn.Linear):
        num_input = m.weight.size(-1)
        m.weight.uniform_(-np.sqrt(6 / num_input) / freq, np.sqrt(6 / num_input) / freq)

  return init


class ModSIREN_Skip_Net(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim,
               out_dim,
               style_dim,
               num_blocks,
               device=None,
               name_prefix='siren_skip',
               add_out_layer=False,
               add_in_layer=False,
               in_layer_mode='siren', # [siren, mod_film]
               xyz_sine_w=20,
               disable_to_rgb=False,
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'input_dim': input_dim,
      'hidden_dim': hidden_dim,
      'out_dim': out_dim,
      'style_dim': style_dim,
      'num_blocks': num_blocks,
      'add_out_layer': add_out_layer,
      'add_in_layer': add_in_layer,
      'in_layer_mode': in_layer_mode,
      'xyz_sine_w': xyz_sine_w,
      'disable_to_rgb': disable_to_rgb,
    }, prefix_str=name_prefix)

    self.device = device
    self.name_prefix = name_prefix
    self.num_blocks = num_blocks
    self.in_layer_mode = in_layer_mode
    self.disable_to_rgb = disable_to_rgb

    if disable_to_rgb:
      self.out_dim = hidden_dim
    else:
      self.out_dim = out_dim

    self.module_name_list = []
    self.style_dim_dict = {}

    if add_in_layer:
      _in_dim = input_dim
      _out_dim = hidden_dim

      if in_layer_mode == 'siren':
        self.in_layer = SirenLayer(input_dim=_in_dim, hidden_dim=_out_dim,
                                   w0=xyz_sine_w, is_first=True)
        self.module_name_list.append('in_layer')
      elif in_layer_mode == 'mod_film':
        from .siren_net import ModFiLMLayer, _first_layer_film_sine_init

        self.in_layer = ModFiLMLayer(in_dim=_in_dim, out_dim=_out_dim, style_dim=style_dim)
        self.in_layer.fc_layer.apply(_first_layer_film_sine_init)
        name = f"{name_prefix}_in"
        self.style_dim_dict[f"w_{name}"] = style_dim
        self.module_name_list.append('in_layer')
      else:
        raise NotImplementedError
    else:
      self.in_layer = None
      _out_dim = input_dim

    blocks = OrderedDict()
    to_rbgs = OrderedDict()
    for idx in range(num_blocks):

      _in_dim = _out_dim
      _out_dim = hidden_dim

      name = f"{name_prefix}_b{idx}"
      _block = ModSirenBlock(in_dim=_in_dim,
                             out_dim=_out_dim,
                             style_dim=style_dim,
                             name_prefix=f'w_{name}')
      self.style_dim_dict.update(_block.style_dim_dict)
      blocks[name] = _block

      _to_rgb = ToRGB(in_dim=_out_dim, dim_rgb=out_dim)
      to_rbgs[name] = _to_rgb

    self.blocks = nn.ModuleDict(blocks)
    self.module_name_list.append('blocks')

    if disable_to_rgb:
      self.to_rgbs = None
    else:
      self.to_rgbs = nn.ModuleDict(to_rbgs)
      self.module_name_list.append('to_rgbs')


    if add_out_layer:
      out_layers = []
      if out_dim > 3:
        out_layers.append(nn.Linear(out_dim, 3))
      out_layers.append(nn.Tanh())

      self.out_layer = nn.Sequential(*out_layers)
      self.out_layer.apply(_frequency_init(100))
      self.module_name_list.append('out_layer')
    else:
      self.out_layer = None

    models_dict = {}
    for name in self.module_name_list:
      models_dict[name] = getattr(self, name)
    models_dict[name_prefix] = self
    logger = logging.getLogger('tl')
    torch_utils.print_number_params(models_dict=models_dict, logger=logger)
    logger.info(self)
    pass

  def forward(self,
              input,
              style_dict,
              block_end_index=None,
              **kwargs):
    """

    :param input: points xyz, (b, num_points, 3)
    :param style_dict:
    :param kwargs:

    :return

    - out: (b, num_points, out_dim)

    """
    if block_end_index is None:
      block_end_index = self.num_blocks

    x = input

    if self.in_layer is not None:
      if self.in_layer_mode == 'siren':
        if global_cfg.tl_debug:
          VerboseModel.forward_verbose(self.in_layer,
                                       inputs_args=(x, ),
                                       name_prefix=f'{self.name_prefix}.in_layer.')
        x = self.in_layer(x)
      elif self.in_layer_mode == 'mod_film':
        name = f"w_{self.name_prefix}_in"
        style_ = style_dict[name]
        if global_cfg.tl_debug:
          VerboseModel.forward_verbose(self.in_layer,
                                       inputs_args=(x, style_),
                                       name_prefix=f'{self.name_prefix}.in_layer.')
        x = self.in_layer(x, style_)
      else:
        raise NotImplementedError

    rgb = None
    for idx, (name, block) in enumerate(self.blocks.items()):

      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(block,
                                     inputs_args=(x, style_dict),
                                     submodels=['mod1', 'mod2'],
                                     name_prefix=f'{name}.')
      x = block(x, style_dict)

      if self.disable_to_rgb:
        rgb = x
      else:
        if global_cfg.tl_debug:
          VerboseModel.forward_verbose(self.to_rgbs[name],
                                       inputs_args=(x, rgb),
                                       name_prefix=f'{name}.to_rgb.')
        rgb = self.to_rgbs[name](x, skip=rgb)

      if idx + 1 == block_end_index:
        break

    if self.out_layer is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.out_layer,
                                     inputs_args=(rgb, ),
                                     name_prefix='out_layer.')
      out = self.out_layer(rgb)
    else:
      out= rgb

    return out


class SigmaMul(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               mul=20.):
    super().__init__()

    self.repr_str = f"mul={mul}"
    self.mul = mul
    pass

  def forward(self, sigma):
    return torch.where(sigma > 0, sigma * self.mul, sigma)


class NeRF_Net(nn.Module):
  """

  """
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               shape_net_cfg={},
               app_net_cfg={},
               name_prefix='nerf',
               shape_block_end_index=None,
               app_block_end_index=None,
               sigma_mul=None,
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'shape_net_cfg': shape_net_cfg,
      'app_net_cfg': app_net_cfg,
      'shape_block_end_index': shape_block_end_index,
      'app_block_end_index': app_block_end_index,
      'sigma_mul': sigma_mul,
    })

    self.shape_net_cfg = shape_net_cfg
    self.app_net_cfg = app_net_cfg
    self.name_prefix = name_prefix
    self.shape_block_end_index = shape_block_end_index
    self.app_block_end_index = app_block_end_index
    self.sigma_mul = sigma_mul

    self.module_name_list = []

    # self.style_dim_dict = {}

    self.shape_net = ModSIREN_Skip_Net(**{
      **shape_net_cfg,
      'name_prefix': 'shape'
    })
    self.style_dim_dict_shape = self.shape_net.style_dim_dict
    self.module_name_list.append('shape_net')

    # _in_dim = shape_net_cfg['out_dim']
    _in_dim = self.shape_net.out_dim

    self.sigma_layer = nn.Linear(_in_dim, 1)
    # self.final_layer.apply(frequency_init(25))
    self.module_name_list.append('sigma_layer')

    if sigma_mul is not None:
      self.sigma_mul_layer = SigmaMul(sigma_mul)
      self.module_name_list.append('sigma_mul_layer')
    else:
      self.sigma_mul_layer = None

    from . import cips_net

    self.app_net = cips_net.CIPSNet(**{
      **app_net_cfg,
      'input_dim': _in_dim,
      'name_prefix': 'app'
    })
    self.style_dim_dict_app = self.app_net.style_dim_dict
    self.module_name_list.append('app_net')

    # self.out_dim = app_net_cfg['out_dim']
    self.out_dim = self.app_net.out_dim

    # self.color_layer_linear = nn.Sequential(
    #   nn.Linear(_out_dim, rgb_dim),
    # )
    # self.color_layer_linear.apply(init_func.kaiming_leaky_init)
    # self.module_name_list.append('color_layer_linear')

    logger = logging.getLogger('tl')
    models_dict = {}
    for name in self.module_name_list:
      models_dict[name] = getattr(self, name)
    models_dict[name_prefix] = self
    torch_utils.print_number_params(models_dict=models_dict, logger=logger)
    logger.info(self)
    pass

  def forward(self,
              x,
              style_dict,
              ray_directions=None,
              **kwargs):
    """

    :param x: points xyz, (b, num_points, 3)
    :param style_dict:
    :param ray_directions: (b, num_points, 3)
    :param kwargs:
    :return

    - out: (b, num_points, rgb_dim + 1), rgb(rgb_dim) + sigma(1)

    """

    # scale xyz

    x = self.shape_net(x, style_dict, block_end_index=self.shape_block_end_index)

    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(self.sigma_layer,
                                   inputs_args=(x, ),
                                   name_prefix="sigma_layer")
    sigma = self.sigma_layer(x)

    if self.sigma_mul_layer is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.sigma_mul_layer,
                                     inputs_args=(sigma, ),
                                     name_prefix="sigma_mul_layer")
      sigma = self.sigma_mul_layer(sigma)

    x = self.app_net(x, style_dict, block_end_index=self.app_block_end_index)

    out = torch.cat([x, sigma], dim=-1)
    return out


