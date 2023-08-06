from itertools import chain
import numpy as np
import os
import argparse
import torch
import torch.distributed as dist

from . import d2_comm


def d2_get_rank():
  return d2_comm.get_rank()


def d2_synchronize():
  d2_comm.synchronize()


def d2_reduce_dict(input_dict,
                   average=True,
                   to_scalar=True):
  """
    Reduce the values in the dictionary from all processes so that process with rank
    0 has the reduced results.

    Args:
        input_dict (dict): inputs to be reduced. All the values must be scalar CUDA Tensor.
        average (bool): whether to do average or sum

    Returns:
        a dict with the same keys as input_dict, after reduction.

  """
  input_dict_tensor = {}
  for k, v in input_dict.items():
    reduced = torch.tensor(v, dtype=torch.float32, device='cuda')
    input_dict_tensor[k] = reduced

  reduced_dict = d2_comm.reduce_dict(input_dict=input_dict_tensor, average=average)

  if d2_comm.get_rank() !=0 :
    reduced_dict = {}

  if to_scalar:
    for k in reduced_dict.keys():
      reduced_dict[k] = reduced_dict[k].item()

  return reduced_dict


def gather_tensor_of_master(tensor,
                            to_cur_device=False):
  """
  Get the tensor of the master.

  :param tensor:
  :param to_cur_device:
  :return:
  """
  tensor_list = d2_comm.all_gather(tensor)
  if to_cur_device:
    ret_tensor = tensor_list[0].to(tensor.device)
  else:
    ret_tensor = tensor_list[0]

  return ret_tensor


def all_gather_to_same_device(data,
                              to_cur_device=False):
  """
  For all members, gather a list of data from each rank.

  :param data:
  :param to_cur_device:
  :return:
  """
  data_list = d2_comm.all_gather(data=data)

  if to_cur_device:
    ret_list = []
    for tensor in data_list:
      ret_list.append(tensor.to(data.device))
  else:
    ret_list = data_list

  return ret_list


def gather_to_same_device(data,
                          dst=0,
                          to_cur_device=False):
  """
  Gather a list of data from each rank. Otherwise, an empty list.

  :param data:
  :param to_cur_device:
  :return:
  """
  data_list = d2_comm.gather(data=data, dst=dst)

  if to_cur_device:
    ret_list = []
    for tensor in data_list:
      ret_list.append(tensor.to(data.device))
  else:
    ret_list = data_list

  return ret_list


def parser_local_rank():
  parser = argparse.ArgumentParser()
  parser.add_argument("--local_rank", type=int, default=0)
  args, _ = parser.parse_known_args()
  return args.local_rank


def is_distributed():
  n_gpu = int(os.environ["WORLD_SIZE"]) if "WORLD_SIZE" in os.environ else 1
  distributed = n_gpu > 1
  return distributed


def get_world_size():
  return d2_comm.get_world_size()


def ddp_init(seed=0):
  """
  use config_cfgnode
  """

  rank = parser_local_rank()
  distributed = is_distributed()

  torch.manual_seed(seed)
  torch.cuda.set_device(rank)

  if distributed:
    torch.distributed.init_process_group(backend="nccl", init_method="env://")
    # important: use different random seed for different process
    torch.manual_seed(seed + dist.get_rank())
    torch.cuda.set_device(rank)
    dist.barrier()

  world_size = d2_comm.get_world_size()

  return rank, world_size


@torch.no_grad()
def sync_gradients(model, world_size):
  if world_size > 1:
    params = [param for param in model.parameters() if param.grad is not None]

    if len(params) > 0:
      grad_flat = torch.cat([param.grad.flatten() for param in params])

      torch.distributed.all_reduce(grad_flat)
      grad_flat.div_(world_size)

      torch.nan_to_num(grad_flat, nan=0, posinf=1e5, neginf=-1e5, out=grad_flat)

      grads = grad_flat.split([param.numel() for param in params])
      for param, grad in zip(params, grads):
        param.grad = grad.reshape(param.shape)

  pass

def sync_models(rank,
                world_size,
                sync_models):
  # Distribute across GPUs.

  if rank == 0:
    print(f'Distributing across {world_size} GPUs...')
  if world_size > 1:
    for module in sync_models:
      for param in chain(module.parameters(), module.buffers()):
        torch.distributed.broadcast(param, src=0)
  pass