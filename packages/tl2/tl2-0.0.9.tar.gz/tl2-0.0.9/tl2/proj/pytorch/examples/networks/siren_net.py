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


class SinAct(nn.Module):
  def __init__(self, ):
    super(SinAct, self).__init__()

  def forward(self, x):
    return torch.sin(x)


class ScaleGradient(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self, gamma=1.):
    """
    Keep the input unchanged but scale the gradients by gamma

    :param gamma:
    """
    super(ScaleGradient, self).__init__()

    self.repr_str = f"gamma={gamma:.3f}=1/{1/gamma:.3f}"

    self.gamma = gamma
    pass

  def forward(self, x):
    return self.gamma * x + (1 - self.gamma) * x.detach()


class ScaleAct(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               gamma=15.,
               beta=30.):
    super(ScaleAct, self).__init__()

    self.repr_str = f"gamma={gamma}, " \
                    f"beta={beta}, "

    self.gamma = gamma
    self.beta = beta
    pass

  def forward(self, x):
    out = x * self.gamma + self.beta
    return out


class ModFiLMLayer(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               in_dim,
               out_dim,
               style_dim,
               freq_scale=15,
               freq_shift=30,
               gradient_scale=None,
               **kwargs):
    super().__init__()

    if gradient_scale is not None and isinstance(gradient_scale, str):
      gradient_scale = eval(gradient_scale)

    self.repr_str = f"in_dim={in_dim}, " \
                    f"out_dim={out_dim}, " \
                    f"style_dim={style_dim}, " \
                    f"freq_scale={freq_scale}, " \
                    f"freq_shift={freq_shift}, " \
                    f"gradient_scale={gradient_scale}"

    self.mod_freq = nn.Linear(style_dim, out_dim)
    self.mod_freq.apply(init_func.kaiming_leaky_init)
    if freq_scale == 1 and freq_shift == 0:
      self.freq_scale = nn.Identity()
    else:
      self.freq_scale = ScaleAct(gamma=freq_scale, beta=freq_shift)

    self.mod_phase = nn.Linear(style_dim, out_dim)
    self.mod_phase.apply(init_func.kaiming_leaky_init)

    self.fc_layer = nn.Linear(in_dim, out_dim)
    self.fc_layer.apply(_frequency_init(25))

    if gradient_scale is not None:
      self.gradient_scale_layer = ScaleGradient(gamma=gradient_scale)
    else:
      self.gradient_scale_layer = None

    self.sin_act = SinAct()
    pass

  def forward(self,
              x,
              style):
    """

    :param x: (b, n, in_dim) or (b, in_dim)
    :param style: (b, style_dim)
    :return

    """

    # (b, out_dim)
    x = self.fc_layer(x)

    # (b, style_dim) -> (b, out_dim)
    freq = self.mod_freq(style)
    freq = self.freq_scale(freq)

    phase = self.mod_phase(style)

    if x.dim() == 3:
      freq = freq.unsqueeze(1)
      phase = phase.unsqueeze(1)
    elif x.dim() == 2:
      pass
    else:
      raise NotImplementedError

    x = freq * x

    if self.gradient_scale_layer is not None:
      _x = self.gradient_scale_layer(x)
      x = _x

    return self.sin_act(x + phase)


def _frequency_init(freq):
  def init(m):
    with torch.no_grad():
      if isinstance(m, nn.Linear):
        num_input = m.weight.size(-1)
        m.weight.uniform_(-np.sqrt(6 / num_input) / freq, np.sqrt(6 / num_input) / freq)

  return init

def _first_layer_film_sine_init(m):
  with torch.no_grad():
    if isinstance(m, nn.Linear):
      num_input = m.weight.size(-1)
      m.weight.uniform_(-1 / num_input, 1 / num_input)


class SkipLayer(nn.Module):
  def __init__(self, ):
    super(SkipLayer, self).__init__()

  def forward(self, x0, x1):
    # out = (x0 + x1) / math.pi
    out = (x0 + x1) / math.sqrt(2)
    return out


class ModFiLMBlock(nn.Module):
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

    self.mod1 = ModFiLMLayer(in_dim=in_dim,
                             out_dim=out_dim,
                             style_dim=style_dim)
    self.style_dim_dict[f'{name_prefix}_0'] = style_dim

    self.mod2 = ModFiLMLayer(in_dim=out_dim,
                             out_dim=out_dim,
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


class SIRENNet_skip(nn.Module):
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
    }, prefix_str=name_prefix)

    self.device = device
    self.name_prefix = name_prefix
    self.num_blocks = num_blocks

    self.module_name_list = []
    self.style_dim_dict = {}

    if add_in_layer:
      _in_dim = input_dim
      _out_dim = hidden_dim
      self.in_layer = ModFiLMLayer(in_dim=_in_dim, out_dim=_out_dim, style_dim=style_dim)
      self.in_layer.fc_layer.apply(_first_layer_film_sine_init)
      name = f"{name_prefix}_in"
      self.style_dim_dict[f"w_{name}"] = style_dim

    else:
      self.in_layer = None
      _out_dim = input_dim

    blocks = OrderedDict()
    to_rbgs = OrderedDict()
    for idx in range(num_blocks):

      _in_dim = _out_dim
      _out_dim = hidden_dim

      name = f"{name_prefix}_b{idx}"
      _block = ModFiLMBlock(in_dim=_in_dim,
                            out_dim=_out_dim,
                            style_dim=style_dim,
                            name_prefix=f'w_{name}')
      self.style_dim_dict.update(_block.style_dim_dict)
      blocks[name] = _block

      _to_rgb = ToRGB(in_dim=_out_dim, dim_rgb=out_dim)
      to_rbgs[name] = _to_rgb

    self.blocks = nn.ModuleDict(blocks)
    self.to_rgbs = nn.ModuleDict(to_rbgs)
    self.to_rgbs.apply(_frequency_init(100))
    self.module_name_list.append('blocks')
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
      name = f"w_{self.name_prefix}_in"
      _style = style_dict[name]

      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.in_layer,
                                     inputs_args=(x, _style),
                                     name_prefix=f'{self.name_prefix}.in_layer.')
      x = self.in_layer(x, _style)

    rgb = None
    for idx, (name, block) in enumerate(self.blocks.items()):

      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(block,
                                     inputs_args=(x, style_dict),
                                     submodels=['mod1', 'mod2'],
                                     name_prefix=f'{name}.')
      x = block(x, style_dict)

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


class PosEncoding(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               N_freqs,
               in_dim=3,
               xyz_affine=False,
               affine_dim=None,
               append_xyz=False,
               **kwargs):
    """
    Defines a function that embeds x to (x, sin(2^k x), cos(2^k x), ...)

    :param max_logscale: 9
    :param N_freqs: 10
    :param logscale:
    :param multi_pi:
    """
    super().__init__()

    self.repr_str = f"N_freqs={N_freqs}, " \
                    f"in_dim={in_dim}, " \
                    f"xyz_affine={xyz_affine}, " \
                    f"affine_dim={affine_dim}, " \
                    f"append_xyz={append_xyz}"

    self.N_freqs = N_freqs
    self.append_xyz = append_xyz

    self.funcs = [torch.sin, torch.cos]

    self.freqs = list(map(lambda x: 2**x * math.pi, range(N_freqs)))

    if xyz_affine:
      assert affine_dim is not None
      self.affine_layer = nn.Linear(in_dim, affine_dim)
      self.in_dim = affine_dim
    else:
      self.affine_layer = None
      self.in_dim = in_dim
    pass

  def get_out_dim(self):
    if self.append_xyz:
      outdim = self.in_dim + self.in_dim * 2 * self.N_freqs
    else:
      outdim = self.in_dim * 2 * self.N_freqs
    return outdim

  def forward(self, x):
    """
    Inputs:
        x: (B, 3)

    Outputs:
        out: (B, 2 * N_freqs * in_dim + in_dim)
    """
    if self.affine_layer is not None:
      x = self.affine_layer(x)

    out = []
    if self.append_xyz:
      out.append(x)
    for func in self.funcs:
      emb_list = list(map(lambda freq: func(freq * x), self.freqs))
      out += emb_list

    emb = torch.cat(out, -1)
    return emb


class ModSIREN_Net(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim,
               out_dim,
               style_dim,
               N_layers,
               device=None,
               name_prefix='siren',
               use_pos_enc=False,
               PEF_cfg={},
               freq_scale=15,
               freq_shift=30,
               gradient_scale=None,
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'input_dim': input_dim,
      'hidden_dim': hidden_dim,
      'out_dim': out_dim,
      'style_dim': style_dim,
      'N_layers': N_layers,
      'use_pos_enc': use_pos_enc,
      'PEF_cfg': PEF_cfg,
      'freq_scale': freq_scale,
      'freq_shift': freq_shift,
      'gradient_scale': gradient_scale,
    }, prefix_str=name_prefix)

    self.device = device
    self.N_layers = N_layers
    self.name_prefix = name_prefix
    self.out_dim = out_dim

    self.module_name_list = []
    self.style_dim_dict = {}

    if use_pos_enc:
      self.pos_enc_layer = PosEncoding(**PEF_cfg)
      self.module_name_list.append('pos_enc_layer')
      _out_dim = self.pos_enc_layer.get_out_dim()

    else:
      self.pos_enc_layer = None
      _out_dim = input_dim

    blocks = OrderedDict()
    for idx in range(N_layers):
      _in_dim = _out_dim
      _out_dim = hidden_dim
      if idx == N_layers - 1:
        _out_dim = out_dim

      _block = ModFiLMLayer(in_dim=_in_dim, out_dim=_out_dim, style_dim=style_dim,
                            freq_scale=freq_scale, freq_shift=freq_shift,
                            gradient_scale=gradient_scale)
      # initialize
      _block.fc_layer.apply(_frequency_init(25))
      if idx == 0:
        _block.fc_layer.apply(_first_layer_film_sine_init)

      name = f"{name_prefix}_{idx}"
      blocks[name] = _block
      self.style_dim_dict[f"w_{name}"] = style_dim
      self.module_name_list.append(f"blocks.{name}")

    self.blocks = nn.ModuleDict(blocks)
    self.module_name_list.append('blocks')

    models_dict = {}
    for name in self.module_name_list:
      models_dict[name] = tl2_utils.attrgetter_default(object=self, attr=name)
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
      block_end_index = self.N_layers

    if self.pos_enc_layer is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.pos_enc_layer,
                                     inputs_args=(input, ),
                                     name_prefix=f'{self.name_prefix}.pos_enc_layer.')
      x = self.pos_enc_layer(input)
    else:
      x = input

    for idx, (name, block) in enumerate(self.blocks.items()):
      style_name = f"w_{name}"
      style = style_dict[style_name]

      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(block,
                                     inputs_args=(x, style),
                                     name_prefix=f'{self.name_prefix}.mod_film_{idx}.')
      x = block(x, style)

      if idx + 1 == block_end_index:
        break

    out = x
    return out


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
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'shape_net_cfg': shape_net_cfg,
      'app_net_cfg': app_net_cfg,
      'shape_block_end_index': shape_block_end_index,
      'app_block_end_index': app_block_end_index,
    })

    self.shape_net_cfg = shape_net_cfg
    self.app_net_cfg = app_net_cfg
    self.name_prefix = name_prefix
    self.shape_block_end_index = shape_block_end_index
    self.app_block_end_index = app_block_end_index

    self.module_name_list = []

    # self.style_dim_dict = {}

    self.shape_net = ModSIREN_Net(**{
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

    x = self.app_net(x, style_dict, block_end_index=self.app_block_end_index)

    out = torch.cat([x, sigma], dim=-1)
    return out


