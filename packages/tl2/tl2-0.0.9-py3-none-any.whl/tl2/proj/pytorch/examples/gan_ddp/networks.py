import logging

import torch
import torch.nn as nn

from tl2.proj.fvcore import MODEL_REGISTRY, global_cfg
from tl2.proj.pytorch import torch_utils
from tl2.proj.pytorch.pytorch_hook import VerboseModel


@MODEL_REGISTRY.register(name_prefix=__name__)
class Generator(nn.Module):
  def __init__(self,
               nz=100,
               ngf=64,
               nc=3,
               ):
    super(Generator, self).__init__()

    self.nz = nz

    self.main = nn.Sequential(
      # input is Z, going into a convolution
      nn.ConvTranspose2d(nz, ngf * 8, 4, 1, 0, bias=False),
      nn.BatchNorm2d(ngf * 8),
      nn.ReLU(True),
      # state size. (ngf*8) x 4 x 4
      nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ngf * 4),
      nn.ReLU(True),
      # state size. (ngf*4) x 8 x 8
      nn.ConvTranspose2d(ngf * 4, ngf * 2, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ngf * 2),
      nn.ReLU(True),
      # state size. (ngf*2) x 16 x 16
      nn.ConvTranspose2d(ngf * 2, ngf, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ngf),
      nn.ReLU(True),
      # state size. (ngf) x 32 x 32
      nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),
      nn.Tanh()
      # state size. (nc) x 64 x 64
    )

    logger = logging.getLogger('tl')
    torch_utils.print_number_params(
      models_dict={
        'G': self
      }, logger=logger)
    pass

  def forward(self, input):
    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(model=self.main,
                                   inputs_args=(input, ),
                                   name_prefix='G.main.')

    output = self.main(input)
    return output

  def get_zs(self, bs, device='cuda'):
    zs = torch.randn(bs, self.nz, 1, 1, device=device)
    return zs


@MODEL_REGISTRY.register(name_prefix=__name__)
class Discriminator(nn.Module):
  def __init__(self,
               nc=3,
               ndf=64,
               ):
    super(Discriminator, self).__init__()

    self.main = nn.Sequential(
      # input is (nc) x 64 x 64
      nn.Conv2d(nc, ndf, 4, 2, 1, bias=False),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf) x 32 x 32
      nn.Conv2d(ndf, ndf * 2, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ndf * 2),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf*2) x 16 x 16
      nn.Conv2d(ndf * 2, ndf * 4, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ndf * 4),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf*4) x 8 x 8
      nn.Conv2d(ndf * 4, ndf * 8, 4, 2, 1, bias=False),
      nn.BatchNorm2d(ndf * 8),
      nn.LeakyReLU(0.2, inplace=True),
      # state size. (ndf*8) x 4 x 4
      nn.Conv2d(ndf * 8, 1, 4, 1, 0, bias=False),
      # nn.Sigmoid()
    )

    logger = logging.getLogger('tl')
    torch_utils.print_number_params(
      models_dict={
        'D': self
      }, logger=logger)
    pass

  def forward(self, input):
    if global_cfg.tl_debug:
      VerboseModel.forward_verbose(model=self.main,
                                   inputs_args=(input,),
                                   name_prefix='D.main.')
    output = self.main(input)
    # out = output.view(-1, 1).squeeze(1)
    out = output.squeeze()

    return out
