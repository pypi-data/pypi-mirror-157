import os

import torch
import torch.distributed as dist

from tl2.launch.launch_utils import update_parser_defaults_from_yaml
from tl2.proj.pytorch.torch_utils import parser_local_rank, is_distributed


def ddp_init():
  """
  use config_cfgnode
  """

  rank = parser_local_rank()

  parser = update_parser_defaults_from_yaml(parser=None, append_local_rank=True,
                                            is_main_process=(rank==0))

  args = parser.parse_args()

  args.distributed = is_distributed()

  if args.distributed:
    torch.cuda.set_device(args.local_rank)
    torch.distributed.init_process_group(backend="nccl", init_method="env://")
    # comm.synchronize()
    dist.barrier()

  # eval(args.run_func)()
  return args


if __name__ == '__main__':
  args = ddp_init()
  pass
