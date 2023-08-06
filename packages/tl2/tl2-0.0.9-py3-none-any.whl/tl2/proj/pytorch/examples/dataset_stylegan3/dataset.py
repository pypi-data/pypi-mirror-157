# Copyright (c) 2021, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""Streaming images and labels from datasets created with dataset_tool.py."""

import os
import numpy as np
import zipfile
import PIL.Image
import json
import logging
from pathlib import Path

import torch

from tl2.proj.fvcore import MODEL_REGISTRY
from tl2 import tl2_utils
from tl2.proj.pil import pil_utils


# try:
#   import pyspng
# except ImportError:
#   pyspng = None


# ----------------------------------------------------------------------------

def get_training_dataloader(dataset,
                            rank,
                            num_gpus,
                            batch_size,
                            num_workers,
                            shuffle=True,
                            sampler_seed=0,
                            pin_memory=True,
                            prefetch_factor=2):

  batch_gpu = batch_size // num_gpus

  if rank == 0:
    repr_str = tl2_utils.dict2string(prefix_str='Data loader', dict_obj={
      'path': dataset._path,
      'rank': rank,
      'num_gpus': num_gpus,
      'batch_size': f"batch_gpu * num_gpus = {batch_gpu} * {num_gpus} = {batch_gpu*num_gpus}",
      'num_workers': num_workers,
      'shuffle': shuffle,
      'sampler_seed': sampler_seed,
      'pin_memory': pin_memory,
      'prefetch_factor': prefetch_factor
    })
    logging.getLogger('tl').info(repr_str)

  training_set_sampler = InfiniteSampler(
    dataset=dataset, rank=rank, num_replicas=num_gpus, seed=sampler_seed, shuffle=shuffle)

  data_loader = torch.utils.data.DataLoader(
    dataset=dataset,
    sampler=training_set_sampler,
    batch_size=batch_gpu,
    num_workers=num_workers,
    pin_memory=pin_memory,
    prefetch_factor=prefetch_factor)

  return data_loader

# ----------------------------------------------------------------------------
def to_norm_tensor(img_tensor, device):
  """

  :param img_tensor: [0, 255]
  :param device:
  :return: [-1, 1]
  """
  return img_tensor.to(device).to(torch.float32) / 127.5 - 1

# ----------------------------------------------------------------------------


class EasyDict(dict):
  """Convenience class that behaves like a dict but allows access with the attribute syntax."""

  def __getattr__(self, name: str):
    try:
      return self[name]
    except KeyError:
      raise AttributeError(name)

  def __setattr__(self, name: str, value) -> None:
    self[name] = value

  def __delattr__(self, name: str) -> None:
    del self[name]


# ----------------------------------------------------------------------------

# Sampler for torch.utils.data.DataLoader that loops over the dataset
# indefinitely, shuffling items as it goes.

class InfiniteSampler(torch.utils.data.Sampler):
  def __init__(self,
               dataset,
               rank=0,
               num_replicas=1,
               shuffle=True,
               seed=0,
               window_size=0.5):

    assert len(dataset) > 0
    assert num_replicas > 0
    assert 0 <= rank < num_replicas
    assert 0 <= window_size <= 1
    super().__init__(dataset)
    self.dataset = dataset
    self.rank = rank
    self.num_replicas = num_replicas
    self.shuffle = shuffle
    self.seed = seed
    self.window_size = window_size
    pass

  def __iter__(self):
    order = np.arange(len(self.dataset))
    rnd = None
    window = 0
    if self.shuffle:
      rnd = np.random.RandomState(self.seed)
      rnd.shuffle(order)
      window = int(np.rint(order.size * self.window_size))

    idx = 0
    while True:
      i = idx % order.size
      if idx % self.num_replicas == self.rank:
        yield order[i]
      if window >= 2:
        j = (i - rnd.randint(window)) % order.size
        order[i], order[j] = order[j], order[i]
      idx += 1
    pass

# ----------------------------------------------------------------------------

class Dataset(torch.utils.data.Dataset):
  def __init__(self,
               name,  # Name of the dataset.
               raw_shape,  # Shape of the raw image data (NCHW).
               max_size=None,  # Artificially limit the size of the dataset. None = no limit. Applied before xflip.
               use_labels=False,  # Enable conditioning labels? False = label dimension is zero.
               xflip=False,  # Artificially double the size of the dataset via x-flips. Applied after max_size.
               random_seed=0,  # Random seed to use when applying max_size.
               **kwargs
               ):
    self._name = name
    self._raw_shape = list(raw_shape)
    self._use_labels = use_labels
    self._raw_labels = None
    self._label_shape = None

    # Apply max_size.
    self._raw_idx = np.arange(self._raw_shape[0], dtype=np.int64)
    if (max_size is not None) and (self._raw_idx.size > max_size):
      np.random.RandomState(random_seed).shuffle(self._raw_idx)
      self._raw_idx = np.sort(self._raw_idx[:max_size])

    # Apply xflip.
    self._xflip = np.zeros(self._raw_idx.size, dtype=np.uint8)
    if xflip:
      self._raw_idx = np.tile(self._raw_idx, 2)
      self._xflip = np.concatenate([self._xflip, np.ones_like(self._xflip)])

  def _get_raw_labels(self):
    if self._raw_labels is None:
      self._raw_labels = self._load_raw_labels() if self._use_labels else None
      if self._raw_labels is None:
        self._raw_labels = np.zeros([self._raw_shape[0], 0], dtype=np.float32)
      assert isinstance(self._raw_labels, np.ndarray)
      assert self._raw_labels.shape[0] == self._raw_shape[0]
      assert self._raw_labels.dtype in [np.float32, np.int64]
      if self._raw_labels.dtype == np.int64:
        assert self._raw_labels.ndim == 1
        assert np.all(self._raw_labels >= 0)
    return self._raw_labels

  def close(self):  # to be overridden by subclass
    pass

  def _load_raw_image(self, raw_idx):  # to be overridden by subclass
    raise NotImplementedError

  def _load_raw_labels(self):  # to be overridden by subclass
    raise NotImplementedError

  def __getstate__(self):
    return dict(self.__dict__, _raw_labels=None)

  def __del__(self):
    try:
      self.close()
    except:
      pass

  def __len__(self):
    return self._raw_idx.size

  def __getitem__(self, idx):
    image = self._load_raw_image(self._raw_idx[idx])
    assert isinstance(image, np.ndarray)
    assert list(image.shape) == self.image_shape
    assert image.dtype == np.uint8
    if self._xflip[idx]:
      assert image.ndim == 3  # CHW
      image = image[:, :, ::-1]
    return image.copy(), self.get_label(idx), idx

  def get_label(self, idx):
    label = self._get_raw_labels()[self._raw_idx[idx]]
    if label.dtype == np.int64:
      onehot = np.zeros(self.label_shape, dtype=np.float32)
      onehot[label] = 1
      label = onehot
    return label.copy()

  def get_details(self, idx):
    d = EasyDict()
    d.raw_idx = int(self._raw_idx[idx])
    d.xflip = (int(self._xflip[idx]) != 0)
    d.raw_label = self._get_raw_labels()[d.raw_idx].copy()
    return d

  @property
  def name(self):
    return self._name

  @property
  def image_shape(self):
    return list(self._raw_shape[1:])

  @property
  def num_channels(self):
    assert len(self.image_shape) == 3  # CHW
    return self.image_shape[0]

  @property
  def resolution(self):
    assert len(self.image_shape) == 3  # CHW
    assert self.image_shape[1] == self.image_shape[2]
    return self.image_shape[1]

  @property
  def label_shape(self):
    if self._label_shape is None:
      raw_labels = self._get_raw_labels()
      if raw_labels.dtype == np.int64:
        self._label_shape = [int(np.max(raw_labels)) + 1]
      else:
        self._label_shape = raw_labels.shape[1:]
    return list(self._label_shape)

  @property
  def label_dim(self):
    assert len(self.label_shape) == 1
    return self.label_shape[0]

  @property
  def has_labels(self):
    return any(x != 0 for x in self.label_shape)

  @property
  def has_onehot_labels(self):
    return self._get_raw_labels().dtype == np.int64


# ----------------------------------------------------------------------------

@MODEL_REGISTRY.register(name="ImageFolderDataset_of_stylegan")
class ImageFolderDataset(Dataset):

  def __repr__(self):
    repr_str = tl2_utils.get_class_repr(self)
    return repr_str

  def __init__(self,
               path,  # Path to directory or zip.
               resize_resolution=None,  # Ensure specific resolution, None = highest available.
               verbose=True,
               **super_kwargs,  # Additional arguments for the Dataset base class.
               ):

    self._path = path
    self._zipfile = None
    self.resize_resolution = resize_resolution

    if os.path.isdir(self._path):
      self._type = 'dir'
      self._all_fnames = {os.path.relpath(os.path.join(root, fname), start=self._path) for root, _dirs, files in
                          os.walk(self._path) for fname in files}
    elif self._file_ext(self._path) == '.zip':
      self._type = 'zip'
      self._all_fnames = set(self._get_zipfile().namelist())
    elif os.path.isfile(self._path):
      self._type = 'file'
      self._all_fnames = {self._path}
    else:
      # raise IOError('Path must point to a directory or zip')
      assert 0, f"{self._path}"

    PIL.Image.init()
    self._image_fnames = sorted(fname for fname in self._all_fnames if self._file_ext(fname) in PIL.Image.EXTENSION)
    if len(self._image_fnames) == 0:
      raise IOError('No image files found in the specified path')

    # name = os.path.splitext(os.path.basename(self._path))[0]
    name = Path(self._path).name
    raw_shape = [len(self._image_fnames)] + list(self._load_raw_image(0).shape)
    # if resolution is not None and (raw_shape[2] != resolution or raw_shape[3] != resolution):
    #   raise IOError('Image files do not match the specified resolution')

    super().__init__(name=name, raw_shape=raw_shape, **super_kwargs)

    self.repr_str = tl2_utils.dict2string(dict_obj={
      'path': path,
      'resize_resolution': resize_resolution,
      'super_kwargs': super_kwargs,
      'length': len(self),
      'resolution': self.resolution,
    }, use_pprint=True)

    if verbose: logging.getLogger('tl').info(self)
    pass

  @staticmethod
  def _file_ext(fname):
    return os.path.splitext(fname)[1].lower()

  def _get_zipfile(self):
    assert self._type == 'zip'
    if self._zipfile is None:
      self._zipfile = zipfile.ZipFile(self._path)
    return self._zipfile

  def _open_file(self, fname):
    if self._type == 'dir':
      return open(os.path.join(self._path, fname), 'rb')
    if self._type == 'zip':
      return self._get_zipfile().open(fname, 'r')
    if self._type == 'file':
      return open(fname, 'rb')
    return None

  def close(self):
    try:
      if self._zipfile is not None:
        self._zipfile.close()
    finally:
      self._zipfile = None

  def __getstate__(self):
    return dict(super().__getstate__(), _zipfile=None)

  def _load_raw_image(self, raw_idx):
    fname = self._image_fnames[raw_idx]
    with self._open_file(fname) as f:
      # if pyspng is not None and self._file_ext(fname) == '.png':
      #   image = pyspng.load(f.read())
      # else:
      #   image = np.array(PIL.Image.open(f))
      img_pil = PIL.Image.open(f).convert('RGB')

      if self.resize_resolution is not None and img_pil.size[0] != self.resize_resolution:
        img_pil = pil_utils.pil_resize(img_pil, size=(self.resize_resolution, self.resize_resolution))
      image = np.array(img_pil)

    # if image.ndim == 2:
    #   image = image[:, :, np.newaxis]  # HW => HWC
    image = image.transpose(2, 0, 1)  # HWC => CHW
    return image

  def _load_raw_labels(self):
    fname = 'dataset.json'
    if fname not in self._all_fnames:
      return None
    with self._open_file(fname) as f:
      labels = json.load(f)['labels']
    if labels is None:
      return None
    labels = dict(labels)
    labels = [labels[fname.replace('\\', '/')] for fname in self._image_fnames]
    labels = np.array(labels)
    labels = labels.astype({1: np.int64, 2: np.float32}[labels.ndim])
    return labels

# ----------------------------------------------------------------------------
