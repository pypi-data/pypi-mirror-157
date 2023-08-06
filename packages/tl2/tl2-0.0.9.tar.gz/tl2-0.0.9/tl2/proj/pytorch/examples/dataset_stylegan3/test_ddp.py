import logging
import json
import tqdm
from time import perf_counter
from pathlib import Path
import argparse
import os
import random
import numpy as np

import torch
import torch.distributed as dist
import torch.utils.data as data_utils
import torchvision.transforms as tv_trans

from tl2.launch.launch_utils import update_parser_defaults_from_yaml, global_cfg
from tl2.modelarts import modelarts_utils, moxing_utils
from tl2.proj.pil import pil_utils
from tl2.proj.skimage import skimage_utils
from tl2.proj.pytorch.ddp import ddp_utils
from tl2.tl2_utils import AverageMeter
from tl2.proj.logger.textlogger import summary_dict2txtfig, global_textlogger
from tl2.proj.fvcore import build_model
from tl2.proj.pytorch.examples.multi_process_main.dataset import ImageListDataset
from tl2.proj.argparser import argparser_utils
from tl2.proj.pytorch import torch_utils
from tl2 import tl2_utils


def build_parser():
  ## runtime arguments
  parser = argparse.ArgumentParser(description='Training configurations.')

  argparser_utils.add_argument_int(parser, name='local_rank', default=0)
  argparser_utils.add_argument_int(parser, name='seed', default=0)
  argparser_utils.add_argument_int(parser, name='num_workers', default=0)

  return parser


def main():

  parser = build_parser()
  args, _ = parser.parse_known_args()

  rank, world_size = ddp_utils.ddp_init(seed=args.seed)
  torch_utils.init_seeds(seed=args.seed, rank=rank)
  device = torch.device('cuda')

  is_main_process = (rank == 0)

  update_parser_defaults_from_yaml(parser, is_main_process=is_main_process)
  logger = logging.getLogger('tl')

  # dataset

  from tl2.proj.fvcore import build_model
  from tl2.proj.pytorch.examples.dataset_stylegan3.dataset import get_training_dataloader, to_norm_tensor

  dataset = build_model(global_cfg.data_cfg)
  data = dataset[0]

  batch_size = 8
  num_workers = 0
  shuffle = True

  data_loader = get_training_dataloader(dataset=dataset, rank=rank, num_gpus=world_size,
                                        batch_size=batch_size, num_workers=num_workers,
                                        shuffle=shuffle,
                                        **global_cfg.data_loader_cfg)

  data_loader_iter = iter(data_loader)

  imgs, _, idx = next(data_loader_iter)

  imgs_norm = to_norm_tensor(imgs, device=device)
  pass





if __name__ == '__main__':
  main()
