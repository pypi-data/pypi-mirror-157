from itertools import chain
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


class SinAct(nn.Module):
  def __init__(self, ):
    super(SinAct, self).__init__()

  def forward(self, x):
    return torch.sin(x)

class MulAdd(nn.Module):
  def __init__(self, ):
    super(MulAdd, self).__init__()

  def forward(self,
              x,
              freq,
              phase_shift):
    """
    :param x: (b, N_points, c)
    :param freq: (b, out_dim)
    :param phase_shift: (b, out_dim)
    :return:
    """
    freq = freq.unsqueeze(1).expand_as(x)
    phase_shift = phase_shift.unsqueeze(1).expand_as(x)

    out = freq * x + phase_shift
    return out

class FiLMLayer(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim):
    super().__init__()
    self.repr_str = f"input_dim={input_dim}, hidden_dim={hidden_dim}"

    self.layer = nn.Linear(input_dim, hidden_dim)

    self.freq_scale_layer = ScaleAct(gamma=15., beta=30.)

    self.muladd_layer = MulAdd()
    self.sin_layer = SinAct()
    pass

  def forward(self,
              x,
              freq,
              phase_shift):
    """

    :param x: (b, N_points, c)
    :param freq: (b, out_dim)
    :param phase_shift: (b, out_dim)
    :return:
    """
    x = self.layer(x)

    freq = self.freq_scale_layer(freq)
    x = self.muladd_layer(x, freq, phase_shift)

    out = self.sin_layer(x)

    return out

def frequency_init(freq):
  def init(m):
    with torch.no_grad():
      if isinstance(m, nn.Linear):
        num_input = m.weight.size(-1)
        m.weight.uniform_(-np.sqrt(6 / num_input) / freq, np.sqrt(6 / num_input) / freq)

  return init

def first_layer_film_sine_init(m):
  with torch.no_grad():
    if isinstance(m, nn.Linear):
      num_input = m.weight.size(-1)
      m.weight.uniform_(-1 / num_input, 1 / num_input)

class UniformBoxWarp(nn.Module):
  def __init__(self, sidelength):
    super().__init__()
    self.scale_factor = 2 / sidelength

  def forward(self, coordinates):
    return coordinates * self.scale_factor


class ShapeNet(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim,
               out_dim,
               N_layers,
               device=None,
               name_prefix='shape',
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'input_dim': input_dim,
      'hidden_dim': hidden_dim,
      'out_dim': out_dim,
      'N_layers': N_layers,
    }, prefix_str=name_prefix)

    self.device = device
    self.N_layers = N_layers
    self.name_prefix = name_prefix
    self.out_dim = out_dim

    self.module_name_list = []
    self.style_dim_dict = {}

    # Don't worry about this, it was added to ensure compatibility with another model. Shouldn't affect performance.
    self.gridwarper = UniformBoxWarp(0.24)
    self.module_name_list.append('gridwarper')

    network = nn.ModuleList()
    _out_dim = input_dim
    for idx in range(N_layers):
      _in_dim = _out_dim
      _out_dim = hidden_dim
      if idx == N_layers - 1:
        _out_dim = out_dim

      _layer = FiLMLayer(_in_dim, _out_dim)
      network.append(_layer)

      w_name = f"w_{name_prefix}_{idx}"
      self.style_dim_dict[f"{w_name}_f"] = _out_dim
      self.style_dim_dict[f"{w_name}_p"] = _out_dim
      self.module_name_list.append(f"network.{idx}")

    self.network = network
    self.module_name_list.append('network')

    self.network.apply(frequency_init(25))
    self.network[0].apply(first_layer_film_sine_init)

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

    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(self.gridwarper,
                                   inputs_args=(input, ),
                                   name_prefix=f'gridwarper.')
    x = self.gridwarper(input)

    for idx, block in enumerate(self.network):
      w_name = f"w_{self.name_prefix}_{idx}"
      freq_name = f"{w_name}_f"
      freq = style_dict[freq_name]
      phase_name = f"{w_name}_p"
      phase_shift = style_dict[phase_name]

      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(block,
                                     inputs_args=(x, freq, phase_shift),
                                     name_prefix=f'{self.name_prefix}.FiLM.{idx}.')
      x = block(x, freq, phase_shift)

      if idx + 1 == block_end_index:
        break

    out = x
    return out


class AppNet(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim,
               out_dim,
               N_layers,
               device=None,
               name_prefix='app',
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'input_dim': input_dim,
      'hidden_dim': hidden_dim,
      'out_dim': out_dim,
      'N_layers': N_layers,
    }, prefix_str=name_prefix)

    self.device = device
    self.N_layers = N_layers
    self.name_prefix = name_prefix
    self.out_dim = out_dim

    self.module_name_list = []
    self.style_dim_dict = {}

    network = nn.ModuleList()
    _out_dim = input_dim + 3 # + direction
    for idx in range(N_layers):
      _in_dim = _out_dim
      _out_dim = hidden_dim
      if idx == N_layers - 1:
        _out_dim = out_dim

      _layer = FiLMLayer(_in_dim, _out_dim)
      network.append(_layer)

      w_name = f"w_{name_prefix}_{idx}"
      self.style_dim_dict[f"{w_name}_f"] = _out_dim
      self.style_dim_dict[f"{w_name}_p"] = _out_dim
      self.module_name_list.append(f"network.{idx}")

    self.network = network
    self.network.apply(frequency_init(25))
    self.module_name_list.append('network')

    _in_dim = _out_dim
    # self.color_layer_linear = nn.Sequential(nn.Linear(_in_dim, 3))
    self.color_layer_linear = nn.Linear(_in_dim, 3)
    self.color_layer_linear.apply(frequency_init(25))
    self.module_name_list.append('color_layer_linear')

    self.sigmoid_layer = nn.Sigmoid()
    self.module_name_list.append('sigmoid_layer')

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
              ray_directions,
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

    x = input

    for idx, block in enumerate(self.network):
      if idx == 0:
        x = torch.cat([ray_directions, x], dim=-1)

      w_name = f"w_{self.name_prefix}_{idx}"
      freq_name = f"{w_name}_f"
      freq = style_dict[freq_name]
      phase_name = f"{w_name}_p"
      phase_shift = style_dict[phase_name]

      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(block,
                                     inputs_args=(x, freq, phase_shift),
                                     name_prefix=f'{self.name_prefix}.FiLM.{idx}.')
      x = block(x, freq, phase_shift)

      if idx + 1 == block_end_index:
        break

    fea = x

    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(self.color_layer_linear,
                                   inputs_args=(fea, ),
                                   name_prefix=f'{self.name_prefix}.color_layer_linear.')
    rgb = self.color_layer_linear(fea)

    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(self.sigmoid_layer,
                                   inputs_args=(rgb, ),
                                   name_prefix=f'{self.name_prefix}.sigmoid_layer.')
    rgb = self.sigmoid_layer(rgb)

    return fea, rgb


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

    self.shape_net = ShapeNet(**{
      **shape_net_cfg,
      'name_prefix': 'shape'
    })
    self.style_dim_dict_shape = self.shape_net.style_dim_dict
    self.module_name_list.append('shape_net')

    _in_dim = self.shape_net.out_dim

    self.sigma_layer = nn.Linear(_in_dim, 1)
    self.sigma_layer.apply(frequency_init(25))
    self.module_name_list.append('sigma_layer')

    self.app_net = AppNet(**{
      **app_net_cfg,
      'input_dim': _in_dim,
      'name_prefix': 'app'
    })
    self.style_dim_dict_app = self.app_net.style_dim_dict
    self.module_name_list.append('app_net')

    self.out_dim = self.app_net.out_dim

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

    fea, rgb = self.app_net(x, style_dict, ray_directions, block_end_index=self.app_block_end_index)

    out = torch.cat([fea, rgb, sigma], dim=-1)
    return out

  def parse_style_dict(self,
                       frequencies,
                       phase_shifts):

    style_dict = collections.OrderedDict()
    style_dim_dict_shape = self.shape_net.style_dim_dict
    style_dim_dict_app = self.app_net.style_dim_dict
    style_list = list(chain(style_dim_dict_shape.items(), style_dim_dict_app.items()))

    _end = 0
    for (name, style_dim) in style_list:
      if name.endswith('_f'):
        _start = _end
        _end += style_dim
        style_dict[name] = frequencies[..., _start:_end]
      elif name.endswith('_p'):
        style_dict[name] = phase_shifts[..., _start:_end]
      else:
        assert 0
    assert _end == frequencies.shape[-1]

    return style_dict

  def parse_weight_dict(self,
                        frequencies,
                        phase_shifts):

    weight_dict = collections.OrderedDict()
    style_dim_dict_shape = self.shape_net.style_dim_dict
    style_dim_dict_app = self.app_net.style_dim_dict
    style_list = list(chain(style_dim_dict_shape.items(), style_dim_dict_app.items()))

    _end = 0
    for (name, style_dim) in style_list:
      if name.endswith('_f'):
        _start = _end
        _end += style_dim
        weight_dict[name] = frequencies[_start:_end]
      elif name.endswith('_p'):
        weight_dict[name] = phase_shifts[_start:_end]
      else:
        assert 0
    assert _end == frequencies.shape[0]

    return weight_dict


def kaiming_leaky_init(m):
  classname = m.__class__.__name__
  if classname.find('Linear') != -1:
    torch.nn.init.kaiming_normal_(m.weight, a=0.2, mode='fan_in', nonlinearity='leaky_relu')


class MappingNetwork(nn.Module):
  def __repr__(self): return tl2_utils.get_class_repr(self)

  def __init__(self,
               z_dim,
               map_hidden_dim,
               map_output_dim,
               N_layers,
               name_prefix='mapping_shape',
               **kwargs):
    super().__init__()
    if isinstance(map_output_dim, str):
      map_output_dim = eval(map_output_dim)

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'z_dim': z_dim,
      'map_hidden_dim': map_hidden_dim,
      'map_output_dim': map_output_dim,
      'N_layers': N_layers,
    }, prefix_str=name_prefix)

    self.module_name_list = []

    network = []
    _out_dim = z_dim
    for idx in range(N_layers):
      _in_dim = _out_dim
      _out_dim = map_hidden_dim
      if idx == N_layers - 1:
        _out_dim = map_output_dim
        _layers = [
          nn.Linear(_in_dim, _out_dim),
        ]
      else:
        _layers = [
          nn.Linear(_in_dim, _out_dim),
          nn.LeakyReLU(0.2, inplace=True)
        ]
      network.extend(_layers)
      self.module_name_list.append(f'network.{idx * 2}')

    self.network = nn.Sequential(*network)
    # initialization
    self.network.apply(kaiming_leaky_init)
    with torch.no_grad():
      self.network[-1].weight *= 0.25
    self.module_name_list.append('network')

    models_dict = {}
    for name in self.module_name_list:
      models_dict[name] = tl2_utils.attrgetter_default(object=self, attr=name)
    models_dict[name_prefix] = self
    logger = logging.getLogger('tl')
    torch_utils.print_number_params(models_dict=models_dict, logger=logger)
    logger.info(self)

    pass

  def forward(self, z):
    frequencies_offsets = self.network(z)
    frequencies = frequencies_offsets[..., :frequencies_offsets.shape[-1] // 2]
    phase_shifts = frequencies_offsets[..., frequencies_offsets.shape[-1] // 2:]

    return frequencies, phase_shifts


class StyleMappingBaseNet(nn.Module):
  def __repr__(self): return tl2_utils.get_class_repr(self)

  def __init__(self,
               z_dim,
               hidden_dim,
               N_layers,
               name_prefix='mapping_base',
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'z_dim': z_dim,
      'hidden_dim': hidden_dim,
      'N_layers': N_layers,
    }, prefix_str=name_prefix)

    self.z_dim = z_dim
    self.out_dim = hidden_dim

    self.module_name_list = []

    network = []
    _out_dim = z_dim
    for idx in range(N_layers):
      _in_dim = _out_dim
      _out_dim = hidden_dim

      _layers = [
        nn.Linear(_in_dim, _out_dim),
        nn.LeakyReLU(0.2, inplace=True)
      ]
      network.extend(_layers)
      self.module_name_list.append(f'network.{idx * 2}')

    self.network = nn.Sequential(*network)
    # initialization
    self.network.apply(kaiming_leaky_init)
    self.module_name_list.append('network')

    tl2_utils.print_repr(self)
    pass

  def forward(self, z):
    fea = self.network(z)
    return fea

class StyleMappingShapeApp(nn.Module):
  def __repr__(self): return tl2_utils.get_class_repr(self)

  def __init__(self,
               style_dim_dict_shape,
               style_dim_dict_app,
               base_cfg={},
               name_prefix='mapping_shape_app',
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'style_dim_dict_shape': style_dim_dict_shape,
      'style_dim_dict_app': style_dim_dict_app,
      'base_cfg': base_cfg,
    }, prefix_str=name_prefix)

    self.module_name_list = []

    self.base_net = StyleMappingBaseNet(**base_cfg)
    self.module_name_list.append('base_net')

    _in_dim = self.base_net.out_dim
    self.z_dim = self.base_net.z_dim

    self.heads = nn.ModuleDict()
    self.shape_layer_names = []
    self.app_layer_names = []

    for style_dim_dict, layer_names in zip([style_dim_dict_shape, style_dim_dict_app],
                                           [self.shape_layer_names, self.app_layer_names]):

      for name, style_dim in style_dim_dict.items():
        _layer = nn.Linear(_in_dim, style_dim)

        _layer.apply(kaiming_leaky_init)
        with torch.no_grad():
          _layer.weight *= 0.25

        self.heads[name] = _layer
        layer_names.append(name)
        # self.module_name_list.append(f"heads.{name}")

    self.module_name_list.append('heads')

    tl2_utils.print_repr(self)
    pass

  def forward(self,
              z_shape,
              z_app=None):

    fea_shape = self.base_net(z_shape)
    if z_app is None:
      fea_app = fea_shape
    else:
      fea_app = self.base_net(z_app)

    style_dict = {}
    for name in self.shape_layer_names:
      _layer = self.heads[name]
      style_dict[name] = _layer(fea_shape)

    for name in self.app_layer_names:
      _layer = self.heads[name]
      style_dict[name] = _layer(fea_app)

    return style_dict