import torch
import torch.nn as nn


def kaiming_leaky_init(m):
  """
  Init the mapping network of StyleGAN.
  fc -> leaky_relu -> fc -> ...
  Note the outputs of each fc, especially when the number of layers increases.

  :param m:
  :return:
  """
  if isinstance(m, nn.Linear):
    torch.nn.init.kaiming_normal_(m.weight, a=0.2, mode='fan_in', nonlinearity='leaky_relu')
