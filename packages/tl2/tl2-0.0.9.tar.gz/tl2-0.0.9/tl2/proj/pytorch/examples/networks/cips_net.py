import collections
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


class ModFC(nn.Module):
  def __repr__(self): return f"{self.__class__.__name__}({self.repr})"

  def __init__(
        self,
        in_channel,
        out_channel,
        kernel_size=1,
        style_dim=None,
        use_style_fc=True,
        demodulate=True,
        use_group_conv=False,
        eps=1e-8,
        **kwargs):
    """

    """
    super().__init__()

    self.repr = f"in_channel={in_channel}, out_channel={out_channel}, kernel_size={kernel_size}, " \
                f"style_dim={style_dim}, use_style_fc={use_style_fc}, demodulate={demodulate}, " \
                f"use_group_conv={use_group_conv}, eps={eps}"

    self.eps = eps
    self.in_channel = in_channel
    self.out_channel = out_channel
    self.kernel_size = kernel_size
    self.style_dim = style_dim
    self.use_style_fc = use_style_fc
    self.demodulate = demodulate
    self.use_group_conv = use_group_conv

    self.padding = kernel_size // 2

    if use_group_conv:
      self.weight = nn.Parameter(torch.randn(1, out_channel, in_channel, kernel_size, kernel_size))
      torch.nn.init.kaiming_normal_(self.weight[0], a=0.2, mode='fan_in', nonlinearity='leaky_relu')
    else:
      assert kernel_size == 1
      self.weight = nn.Parameter(torch.randn(1, in_channel, out_channel))
      torch.nn.init.kaiming_normal_(self.weight[0], a=0.2, mode='fan_in', nonlinearity='leaky_relu')

    if use_style_fc:
      # self.modulation = EqualLinear(style_dim, in_channel, bias_init=1, lr_mul=1., scale=scale)
      self.modulation = nn.Linear(style_dim, in_channel)
      self.modulation.apply(init_func.kaiming_leaky_init)
      # self.modulation.weight.data.div_(0.01)
    else:
      self.style_dim = in_channel


    pass

  def forward_bmm(self,
                  x,
                  style,
                  weight):
    """

    :param input: (b, in_c, h, w), (b, in_c), (b, n, in_c)
    :param style: (b, in_c)
    :return:
    """
    assert x.shape[0] == style.shape[0]
    if x.dim() == 2:
      input = rearrange(x, "b c -> b 1 c")
    elif x.dim() == 3:
      input = x
    else:
      assert 0

    batch, N, in_channel = input.shape

    if self.use_style_fc:
      # style = self.sin(style)
      style = self.modulation(style)
      # style = self.norm(style)
      style = style.view(-1, in_channel, 1)
    else:
      # style = self.norm(style)
      style = rearrange(style, 'b c -> b c 1')
      # style = style + 1.

    # (1, in, out) * (b in 1) -> (b, in, out)
    weight = weight * (style + 1)

    if self.demodulate:
      demod = torch.rsqrt(weight.pow(2).sum([1, ])).clamp_min(self.eps)  # (b, out)
      weight = weight * demod.view(batch, 1, self.out_channel)  # (b, in, out) * (b, 1, out) -> (b, in, out)
    # (b, n, in) * (b, in, out) -> (b, n, out)
    out = torch.bmm(input, weight)

    if x.dim() == 2:
      out = rearrange(out, "b 1 c -> b c")
    elif x.dim() == 3:
      # out = rearrange(out, "b n c -> b n c")
      pass
    return out

  def forward_group_conv(self,
                         x,
                         style):
    """

    :param input: (b, in_c, h, w), (b, in_c), (b, n, in_c)
    :param style: (b, in_c)
    :return:
    """
    assert x.shape[0] == style.shape[0]
    if x.dim() == 2:
      input = rearrange(x, "b c -> b c 1 1")
    elif x.dim() == 3:
      input = rearrange(x, "b n c -> b c n 1")
    elif x.dim() == 4:
      input = x
    else:
      assert 0

    batch, in_channel, height, width = input.shape

    if self.use_style_fc:
      style = self.modulation(style).view(-1, 1, in_channel, 1, 1)
      style = style + 1.
    else:
      style = rearrange(style, 'b c -> b 1 c 1 1')
      # style = style + 1.
    # (1, out, in, ks, ks) * (b, 1, in, 1, 1) -> (b, out, in, ks, ks)
    weight = self.weight * style
    if self.demodulate:
      demod = torch.rsqrt(weight.pow(2).sum([2, 3, 4])).clamp_min(self.eps) # (b, out)
      weight = weight * demod.view(batch, self.out_channel, 1, 1, 1) # (b, out, in, ks, ks) * (b, out, 1, 1, 1)
    # (b*out, in, ks, ks)
    weight = weight.view(batch * self.out_channel, in_channel, self.kernel_size, self.kernel_size)
    # (1, b*in, h, w)
    input = input.reshape(1, batch * in_channel, height, width)
    out = F.conv2d(input, weight, padding=self.padding, groups=batch)
    _, _, height, width = out.shape
    out = out.view(batch, self.out_channel, height, width)

    if x.dim() == 2:
      out = rearrange(out, "b c 1 1 -> b c")
    elif x.dim() == 3:
      out = rearrange(out, "b c n 1 -> b n c")

    return out

  def forward(self,
              x,
              style,
              force_bmm=False):
    """

    :param input: (b, in_c, h, w), (b, in_c), (b, n, in_c)
    :param style: (b, in_c)
    :return:
    """
    if self.use_group_conv:
      if force_bmm:
        weight = rearrange(self.weight, "1 out in 1 1 -> 1 in out")
        out = self.forward_bmm(x=x, style=style, weight=weight)
      else:
        out = self.forward_group_conv(x=x, style=style)
    else:
      out = self.forward_bmm(x=x, style=style, weight=self.weight)
    return out


class SkipLayer(nn.Module):
  def __init__(self, ):
    super(SkipLayer, self).__init__()

  def forward(self, x0, x1):
    # out = (x0 + x1) / math.pi
    out = (x0 + x1)
    return out


class ModFCBlock(nn.Module):
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

    self.mod1 = ModFC(in_channel=in_dim,
                      out_channel=out_dim,
                      style_dim=style_dim,
                      use_style_fc=True,
                      )
    self.style_dim_dict[f'{name_prefix}_0'] = self.mod1.style_dim
    self.act1 = nn.LeakyReLU(0.2, inplace=True)

    self.mod2 = ModFC(in_channel=out_dim,
                      out_channel=out_dim,
                      style_dim=style_dim,
                      use_style_fc=True,
                      )
    self.style_dim_dict[f'{name_prefix}_1'] = self.mod2.style_dim
    self.act2 = nn.LeakyReLU(0.2, inplace=True)

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
    x = self.act1(x)

    style = style_dict[f'{self.name_prefix}_1']
    x = self.mod2(x, style)
    out = self.act2(x)

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


class CIPSNet(nn.Module):
  def __repr__(self):
    return tl2_utils.get_class_repr(self)

  def __init__(self,
               input_dim,
               hidden_dim,
               out_dim,
               style_dim,
               num_blocks,
               device=None,
               name_prefix='cips',
               add_out_layer=False,
               disable_to_rgb=False,
               skip=True,
               **kwargs):
    super().__init__()

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'input_dim': input_dim,
      'hidden_dim': hidden_dim,
      'out_dim': out_dim,
      'style_dim': style_dim,
      'num_blocks': num_blocks,
      'add_out_layer': add_out_layer,
      'disable_to_rgb': disable_to_rgb,
      'skip': skip,
    }, prefix_str=name_prefix)

    self.device = device
    self.name_prefix = name_prefix
    self.num_blocks = num_blocks
    self.disable_to_rgb = disable_to_rgb
    self.skip = skip

    if disable_to_rgb:
      self.out_dim = hidden_dim
    else:
      self.out_dim = out_dim

    self.channels = {}
    for i in range(num_blocks):
      self.channels[f"w_{name_prefix}_b{i}"] = hidden_dim

    self.module_name_list = []

    self.style_dim_dict = {}

    _out_dim = input_dim

    blocks = OrderedDict()
    to_rbgs = OrderedDict()
    for i, (name, channel) in enumerate(self.channels.items()):
      _in_dim = _out_dim
      _out_dim = channel

      _block = ModFCBlock(in_dim=_in_dim,
                          out_dim=_out_dim,
                          style_dim=style_dim,
                          name_prefix=f'{name}')
      self.style_dim_dict.update(_block.style_dim_dict)
      blocks[name] = _block

      _to_rgb = ToRGB(in_dim=_out_dim, dim_rgb=out_dim)
      to_rbgs[name] = _to_rgb

    self.blocks = nn.ModuleDict(blocks)
    self.module_name_list.append('blocks')

    if self.disable_to_rgb:
      self.to_rgbs = None
    else:
      self.to_rgbs = nn.ModuleDict(to_rbgs)
      self.to_rgbs.apply(_frequency_init(100))
      self.module_name_list.append('to_rgbs')

    if add_out_layer:
      out_layers = []
      if out_dim > 3:
        out_layers.append(nn.Linear(out_dim, 3))
      out_layers.append(nn.Tanh())

      self.out_layer = nn.Sequential(*out_layers)
      self.out_layer.apply(_frequency_init(100))
      self.module_name_list.append('out_layer')

      self.hidden_layer = nn.Linear(input_dim, out_dim)
      self.module_name_list.append('hidden_layer')

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

    - out: (b, num_points, 4), rgb(3) + sigma(1)

    """
    if block_end_index is None:
      block_end_index = self.num_blocks

    x = input

    if block_end_index > 0:
      rgb = None
      for idx, (name, block) in enumerate(self.blocks.items()):

        if global_cfg.tl_debug:
          VerboseModel.forward_verbose(block,
                                       inputs_args=(x, style_dict, self.skip),
                                       submodels=['mod1', 'mod2'],
                                       name_prefix=f'{self.name_prefix}.b.{idx}.')
        x = block(x, style_dict, skip=self.skip)

        if self.disable_to_rgb:
          rgb = x
        else:
          if global_cfg.tl_debug:
            VerboseModel.forward_verbose(self.to_rgbs[name],
                                         inputs_args=(x, rgb),
                                         name_prefix=f'{self.name_prefix}.to_rgb.{idx}.')
          rgb = self.to_rgbs[name](x, skip=rgb)

        if idx + 1 >= block_end_index:
          break
    else:
      rgb = self.hidden_layer(x)

    if self.out_layer is not None:
      if global_cfg.tl_debug:
        VerboseModel.forward_verbose(self.out_layer,
                                     inputs_args=(rgb, ),
                                     name_prefix='out_layer.')
      out = self.out_layer(rgb)
    else:
      out= rgb

    return out

