import os
import logging
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Tuple

import torch.nn as nn
import torch

from fvcore.common.checkpoint import Checkpointer as Checkpointer_base
from fvcore.common.checkpoint import _IncompatibleKeys, _strip_prefix_if_present

from .logger import setup_logger

__all__ = ['Checkpointer', ]


class Checkpointer(Checkpointer_base):
  """
  *: https://www.zhihu.com/question/287097169

  """
  def __init__(self,
               model: nn.Module,
               save_dir: str = "",
               *,
               distributed_rank=0,
               save_to_disk: bool = True,
               **checkpointables: object,
               ):
    """
    Args:
        model (nn.Module): model.
        save_dir (str): a directory to save and find checkpoints.
        save_to_disk (bool): if True, save checkpoint to disk, otherwise
            disable saving for this checkpointer.
        checkpointables (object): any checkpointable objects, i.e., objects
            that have the `state_dict()` and `load_state_dict()` method. For
            example, it can be used like
            `Checkpointer(model, "dir", optimizer=optimizer)`.
    """
    self.distributed_rank = distributed_rank

    if save_dir:
      os.makedirs(save_dir, exist_ok=True)

    self.logger = logging.getLogger('fvcore')
    if len(self.logger.handlers) == 0:
      self.logger = setup_logger(output=save_dir, name='fvcore', distributed_rank=distributed_rank)

    super(Checkpointer, self).__init__(
      model=model,
      save_dir=save_dir,
      save_to_disk=save_to_disk,
      **checkpointables)
    pass

  def save(self, name: str, **kwargs: Dict[str, str]) -> None:
    """
    Dump model and checkpointables to a file.

    Args:
        name (str): name of the file.
        kwargs (dict): extra arbitrary data to save.
    """
    # if self.distributed_rank != 0:
    #   return

    return super(Checkpointer, self).save(name=name, **kwargs)

  def has_checkpoint(self) -> bool:
    """
    Returns:
        bool: whether a checkpoint exists in the target directory.
    """
    return super(Checkpointer, self).has_checkpoint()

  def get_checkpoint_file(self) -> str:
    """
    Returns:
        str: The latest checkpoint file in target directory.
    """
    return super(Checkpointer, self).get_checkpoint_file()

  def _load_state_dict(self, checkpoint_state_dict) -> _IncompatibleKeys:  # pyre-ignore
    """
    Load weights from a checkpoint.

    Args:
        checkpoint (Any): checkpoint contains the weights.

    Returns:
        ``NamedTuple`` with ``missing_keys``, ``unexpected_keys``,
            and ``incorrect_shapes`` fields:
            * **missing_keys** is a list of str containing the missing keys
            * **unexpected_keys** is a list of str containing the unexpected keys
            * **incorrect_shapes** is a list of (key, shape in checkpoint, shape in model)

        This is just like the return value of
        :func:`torch.nn.Module.load_state_dict`, but with extra support
        for ``incorrect_shapes``.
    """
    self._convert_ndarray_to_tensor(checkpoint_state_dict)

    # if the state_dict comes from a model that was wrapped in a
    # DataParallel or DistributedDataParallel during serialization,
    # remove the "module" prefix before performing the matching.
    _strip_prefix_if_present(checkpoint_state_dict, "module.")

    # work around https://github.com/pytorch/pytorch/issues/24139
    model_state_dict = self.model.state_dict()
    incorrect_shapes = []
    for k in list(checkpoint_state_dict.keys()):
      if k in model_state_dict:
        shape_model = tuple(model_state_dict[k].shape)
        shape_checkpoint = tuple(checkpoint_state_dict[k].shape)
        if shape_model != shape_checkpoint:
          incorrect_shapes.append((k, shape_checkpoint, shape_model))
          checkpoint_state_dict.pop(k)
    # pyre-ignore
    incompatible = self.model.load_state_dict(checkpoint_state_dict, strict=False)
    return _IncompatibleKeys(
      missing_keys=incompatible.missing_keys,
      unexpected_keys=incompatible.unexpected_keys,
      incorrect_shapes=incorrect_shapes,
    )

  def load_state_dict(self,
                      checkpoint_state_dict):
    """
    Load from the given checkpoint. When path points to network file, this
    function has to be called on all ranks.

    Args:
        path (str): path or url to the checkpoint. If empty, will not load
            anything.
        checkpointables (list): List of checkpointable names to load. If not
            specified (None), will load all the possible checkpointables.
    Returns:
        dict:
            extra data loaded from the checkpoint that has not been
            processed. For example, those saved with
            :meth:`.save(**extra_data)`.
    """

    incompatible = self._load_state_dict(checkpoint_state_dict)
    if (
          incompatible is not None
    ):  # handle some existing subclasses that returns None
      self._log_incompatible_keys(incompatible)

    # return any further checkpoint data
    return incompatible

  def load_state_dict_from_file(self,
                                model_path,
                                rank=0):
    self.logger.info(f"Rank {rank} loading checkpoint from {model_path}")
    if not os.path.isfile(model_path):
      assert os.path.isfile(model_path), "Checkpoint {} not found!".format(model_path)

    map_location = lambda storage, loc: storage.cuda(rank)
    checkpoint_state_dict = torch.load(model_path, map_location=map_location)
    return self.load_state_dict(checkpoint_state_dict)


