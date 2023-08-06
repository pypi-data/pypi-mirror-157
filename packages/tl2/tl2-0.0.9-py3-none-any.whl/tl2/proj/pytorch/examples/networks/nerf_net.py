import math
import logging
from collections import OrderedDict
from einops import rearrange

import torch
import torch.nn as nn

from tl2 import tl2_utils
from tl2.proj.pytorch import init_func
from tl2.proj.pytorch import torch_utils
from tl2.proj.fvcore import global_cfg
from tl2.proj.pytorch.pytorch_hook import VerboseModel

from .cips_net import CIPSNet
from .multi_head_mapping import MultiHeadMappingNetwork
from .siren_net import SIRENNet_skip


class UniformBoxWarp(nn.Module):
  def __init__(self, scale_factor):
    super().__init__()
    self.scale_factor = scale_factor
    pass

  def forward(self, coordinates):
    return coordinates * self.scale_factor


class PosEmbedding(nn.Module):
  def __init__(self,
               N_freqs,
               in_dim=3,
               affine_dim=None,
               xyz_affine=False,
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


class NeRFNetwork_CIPS(nn.Module):
  """Adds a UniformBoxWarp to scale input points to -1, 1"""

  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               scale_factor=None,
               PEF_cfg={},
               use_PEF=True,
               shape_net_cfg={},
               app_net_cfg={},
               name_prefix='nerf',
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'scale_factor': scale_factor,
      'PEF_cfg': PEF_cfg,
      'use_PEF': use_PEF,
      'shape_net_cfg': shape_net_cfg,
      'app_net_cfg': app_net_cfg,
    })

    self.name_prefix = name_prefix

    self.module_name_list = []

    if scale_factor is not None:
      self.gridwarper = UniformBoxWarp(scale_factor=scale_factor)
      self.module_name_list.append('gridwarper')
    else:
      self.gridwarper = None

    if use_PEF:
      self.xyz_emb = PosEmbedding(**PEF_cfg)
      _in_dim = self.xyz_emb.get_out_dim()
      self.module_name_list.append('xyz_emb')
      # self.dir_emb = pigan_utils.PosEmbedding(max_logscale=3, N_freqs=4)
      # dim_dir_emb = self.dir_emb.get_out_dim()
    else:
      self.xyz_emb = None
      _in_dim = 3

    _out_dim = shape_net_cfg['input_dim']
    self.in_layer = nn.Linear(_in_dim, _out_dim)
    self.module_name_list.append('in_layer')

    # self.style_dim_dict = {}

    self.shape_net = CIPSNet(**{
      **shape_net_cfg,
      'name_prefix': 'shape'
    })
    self.style_dim_dict_shape = self.shape_net.style_dim_dict
    self.module_name_list.append('shape_net')

    _in_dim = shape_net_cfg['out_dim']

    self.sigma_layer = nn.Linear(_in_dim, 1)
    # self.final_layer.apply(frequency_init(25))
    self.module_name_list.append('sigma_layer')

    self.app_net = CIPSNet(**{
      **app_net_cfg,
      'input_dim': _in_dim,
      'name_prefix': 'app'
    })
    self.style_dim_dict_app = self.app_net.style_dim_dict
    self.module_name_list.append('app_net')

    _in_dim = app_net_cfg['out_dim']
    self.out_dim = _in_dim

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
    if self.gridwarper is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.gridwarper,
                                     inputs_args=(x,),
                                     name_prefix="gridwarper.")
      x = self.gridwarper(x)

    if self.xyz_emb is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.xyz_emb,
                                     inputs_args=(x, ),
                                     name_prefix="xyz_emb.")
      x = self.xyz_emb(x)

    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(self.in_layer,
                                   inputs_args=(x,),
                                   name_prefix="in_layer.")
    x = self.in_layer(x)

    x = self.shape_net(x, style_dict)

    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(self.sigma_layer,
                                   inputs_args=(x, ),
                                   name_prefix="sigma_layer")
    sigma = self.sigma_layer(x)

    x = self.app_net(x, style_dict)

    out = torch.cat([x, sigma], dim=-1)
    return out

  # def print_number_params(self):
  #   print()
  #
  #   pass
  #
  # def get_freq_phase(self, style_dict, name):
  #   styles = style_dict[name]
  #   styles = rearrange(styles, "b (n d) -> b d n", n=2)
  #   frequencies, phase_shifts = styles.unbind(-1)
  #   frequencies = frequencies * 15 + 30
  #   return frequencies, phase_shifts
  #
  # def staged_forward(self,
  #                    transformed_points,
  #                    transformed_ray_directions_expanded,
  #                    style_dict,
  #                    max_points,
  #                    num_steps,
  #                    ):
  #
  #   batch_size, num_points, _ = transformed_points.shape
  #
  #   rgb_sigma_output = torch.zeros((batch_size, num_points, self.rgb_dim + 1),
  #                                  device=self.device)
  #   for b in range(batch_size):
  #     head = 0
  #     while head < num_points:
  #       tail = head + max_points
  #       rgb_sigma_output[b:b + 1, head:tail] = self(
  #         input=transformed_points[b:b + 1, head:tail],  # (b, h x w x s, 3)
  #         style_dict={name: style[b:b + 1] for name, style in style_dict.items()},
  #         ray_directions=transformed_ray_directions_expanded[b:b + 1, head:tail])
  #       head += max_points
  #   rgb_sigma_output = rearrange(rgb_sigma_output, "b (hw s) rgb_sigma -> b hw s rgb_sigma", s=num_steps)
  #   return rgb_sigma_output


class NeRFNetwork_SIREN_skip(nn.Module):
  """
  shape app: SIRENNet_skip, cips_net

  """


  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               scale_factor=None,
               PEF_cfg={},
               use_PEF=True,
               shape_net_cfg={},
               app_net_cfg={},
               name_prefix='nerf',
               shape_block_end_index=None,
               app_block_end_index=None,
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'scale_factor': scale_factor,
      'PEF_cfg': PEF_cfg,
      'use_PEF': use_PEF,
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

    if scale_factor is not None:
      self.gridwarper = UniformBoxWarp(scale_factor=scale_factor)
      self.module_name_list.append('gridwarper')
    else:
      self.gridwarper = None

    if use_PEF:
      self.xyz_emb = PosEmbedding(**PEF_cfg)
      _in_dim = self.xyz_emb.get_out_dim()
      self.module_name_list.append('xyz_emb')
      # self.dir_emb = pigan_utils.PosEmbedding(max_logscale=3, N_freqs=4)
      # dim_dir_emb = self.dir_emb.get_out_dim()
    else:
      self.xyz_emb = None
      _in_dim = 3

    # self.style_dim_dict = {}

    self.shape_net = SIRENNet_skip(**{
      **shape_net_cfg,
      'name_prefix': 'shape'
    })
    self.style_dim_dict_shape = self.shape_net.style_dim_dict
    self.module_name_list.append('shape_net')

    _in_dim = shape_net_cfg['out_dim']

    self.sigma_layer = nn.Linear(_in_dim, 1)
    # self.final_layer.apply(frequency_init(25))
    self.module_name_list.append('sigma_layer')

    self.app_net = CIPSNet(**{
      **app_net_cfg,
      'input_dim': _in_dim,
      'name_prefix': 'app'
    })
    self.style_dim_dict_app = self.app_net.style_dim_dict
    self.module_name_list.append('app_net')

    _in_dim = app_net_cfg['out_dim']
    self.out_dim = _in_dim

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
    if self.gridwarper is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.gridwarper,
                                     inputs_args=(x,),
                                     name_prefix="gridwarper.")
      x = self.gridwarper(x)

    if self.xyz_emb is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.xyz_emb,
                                     inputs_args=(x, ),
                                     name_prefix="xyz_emb.")
      x = self.xyz_emb(x)

    x = self.shape_net(x, style_dict, block_end_index=self.shape_block_end_index)

    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(self.sigma_layer,
                                   inputs_args=(x, ),
                                   name_prefix="sigma_layer")
    sigma = self.sigma_layer(x)

    x = self.app_net(x, style_dict, block_end_index=self.app_block_end_index)

    out = torch.cat([x, sigma], dim=-1)
    return out

  # def print_number_params(self):
  #   print()
  #
  #   pass
  #
  # def get_freq_phase(self, style_dict, name):
  #   styles = style_dict[name]
  #   styles = rearrange(styles, "b (n d) -> b d n", n=2)
  #   frequencies, phase_shifts = styles.unbind(-1)
  #   frequencies = frequencies * 15 + 30
  #   return frequencies, phase_shifts
  #
  # def staged_forward(self,
  #                    transformed_points,
  #                    transformed_ray_directions_expanded,
  #                    style_dict,
  #                    max_points,
  #                    num_steps,
  #                    ):
  #
  #   batch_size, num_points, _ = transformed_points.shape
  #
  #   rgb_sigma_output = torch.zeros((batch_size, num_points, self.rgb_dim + 1),
  #                                  device=self.device)
  #   for b in range(batch_size):
  #     head = 0
  #     while head < num_points:
  #       tail = head + max_points
  #       rgb_sigma_output[b:b + 1, head:tail] = self(
  #         input=transformed_points[b:b + 1, head:tail],  # (b, h x w x s, 3)
  #         style_dict={name: style[b:b + 1] for name, style in style_dict.items()},
  #         ray_directions=transformed_ray_directions_expanded[b:b + 1, head:tail])
  #       head += max_points
  #   rgb_sigma_output = rearrange(rgb_sigma_output, "b (hw s) rgb_sigma -> b hw s rgb_sigma", s=num_steps)
  #   return rgb_sigma_output

