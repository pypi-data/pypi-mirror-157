import logging
import os
import glob
import PIL
import random
import math
import pickle
import numpy as np

import torch
from torch.utils.data import DataLoader, Dataset
import torchvision
from torchvision.datasets import CIFAR10 as CIFAR10_base
import torchvision.transforms as transforms

from tl2.tl2_utils import read_image_list_from_files
from tl2.proj.fvcore import MODEL_REGISTRY


@MODEL_REGISTRY.register(name_prefix=__name__)
class CIFAR10(CIFAR10_base):

  def __init__(
        self,
        root: str,
        img_size,
        horizontal_flip=True,
        train: bool = True,
        transform=None,
        download=True,
  ):
    super(CIFAR10, self).__init__(root=root, train=train, transform=transform, download=download)

    if horizontal_flip:
      self.transform = transforms.Compose(
        [
          transforms.ToTensor(),
          transforms.Normalize([0.5], [0.5]),
          transforms.RandomHorizontalFlip(p=0.5),
          # transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR, antialias=True),
          transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR)
        ])
    else:
      self.transform = transforms.Compose(
        [
          transforms.ToTensor(),
          transforms.Normalize([0.5], [0.5]),
          # transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR, antialias=True),
          transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR)
        ])

    logger = logging.getLogger('tl')
    logger.info(f"\nNum of images ({self.__class__.__name__}):\n {len(self)}")

    pass



@MODEL_REGISTRY.register(name_prefix=__name__)
class ImageList(Dataset):
  """
  python3 -m tl2.tools.get_data_list     \
    --source_dir datasets/ffhq/downsample_ffhq_256x256/  \
    --outfile datasets/ffhq/ffhq_256.txt  \
    --ext *.png
  """

  def __init__(self,
               img_size,
               image_list_file="datasets/ffhq/ffhq_256.txt",
               verbose=False,
               horizontal_flip=True,
               **kwargs):
    super().__init__()

    self.verbose = verbose
    self.image_list = read_image_list_from_files(image_list_file, compress=True)

    assert len(self.image_list) > 0, "Can't find data; make sure you specify the path to your dataset"
    if horizontal_flip:
      self.transform = transforms.Compose(
        [
          transforms.ToTensor(),
          transforms.Normalize([0.5], [0.5]),
          transforms.RandomHorizontalFlip(p=0.5),
          # transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR, antialias=True),
          transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR)
        ])
    else:
      self.transform = transforms.Compose(
        [
          transforms.ToTensor(),
          transforms.Normalize([0.5], [0.5]),
          # transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR, antialias=True),
          transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR)
        ])

    logger = logging.getLogger('tl')
    logger.info(f"\nNum of images ({image_list_file}):\n {len(self)}")
    pass

  def __len__(self):
    return len(self.image_list)

  def __getitem__(self, index):
    image_path = self.image_list[index]
    X = PIL.Image.open(image_path)
    X = self.transform(X)

    if self.verbose:
      return X, image_path
    else:
      return X, 0


def get_dataset(name, subsample=None, batch_size=1, shuffle=True, **kwargs):
    dataset = globals()[name](**kwargs)

    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=True,
        pin_memory=False,
        num_workers=8
    )
    return dataloader, 3

def get_dataloader_distributed(
      dataset,
      batch_size,
      rank=0,
      world_size=1,
      num_workers=0,
      shuffle=True,
      drop_last=True,
      **kwargs):

    sampler = torch.utils.data.distributed.DistributedSampler(
      dataset,
      num_replicas=world_size,
      rank=rank,
      shuffle=shuffle,
    )

    dataloader = torch.utils.data.DataLoader(
        dataset,
        sampler=sampler,
        batch_size=batch_size,
        drop_last=drop_last,
        pin_memory=True,
        num_workers=num_workers,
    )

    return dataloader, sampler
