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
from tl2.modelarts import modelarts_utils
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


def get_dataset(image_list_file,
                distributed,
                num_workers=0,
                debug=False):

  dataset = ImageListDataset(meta_file=image_list_file, )

  if distributed:
    sampler = torch.utils.data.distributed.DistributedSampler(dataset, shuffle=False)
  else:
    sampler = None

  data_loader = data_utils.DataLoader(
    dataset,
    batch_size=1,
    shuffle=False,
    sampler=sampler,
    num_workers=num_workers,
    pin_memory=False)

  if global_cfg.tl_debug:
    data_iter = iter(data_loader)
    data = next(data_iter)

  num_images = len(dataset)
  return data_loader, num_images


def main():

  parser = build_parser()
  args, _ = parser.parse_known_args()

  rank, world_size = ddp_utils.ddp_init(seed=args.seed)
  torch_utils.init_seeds(seed=args.seed, rank=rank)
  device = torch.device('cuda')

  is_main_process = (rank == 0)

  update_parser_defaults_from_yaml(parser, is_main_process=is_main_process)
  logger = logging.getLogger('tl')
  if is_main_process:
    modelarts_utils.setup_tl_outdir_obs(global_cfg)
    modelarts_utils.modelarts_sync_results_dir(global_cfg, join=True)
    modelarts_utils.prepare_dataset(global_cfg.get('modelarts_download', {}), global_cfg=global_cfg)

  # dataset
  distributed = ddp_utils.is_distributed()
  data_loader, num_images = get_dataset(image_list_file=global_cfg.image_list_file,
                                        distributed=distributed,
                                        num_workers=args.num_workers,
                                        debug=global_cfg.tl_debug)

  # projector = build_model(
  #   cfg=global_cfg.model_cfg,
  #   kwargs_priority=True,
  #   cfg_to_kwargs=True,
  #   network_pkl=global_cfg.network_pkl,
  #   loss_cfg=global_cfg.loss_cfg,
  # )

  if rank == 0:
    pbar = tqdm.tqdm(desc=global_cfg.tl_outdir, total=num_images)

  # lpips_metric = skimage_utils.LPIPS(device=device)

  avg_recorder_dict = {}
  for idx, image_path in enumerate(data_loader):
    if rank == 0:
      pbar.update(world_size)

    # ret = ddp_utils.all_gather_to_same_device(image_path)
    image_path = Path(image_path[0])

    outdir = f"{global_cfg.tl_outdir}/exp/{image_path.stem}"
    os.makedirs(outdir, exist_ok=True)

    metric_dict = {
      'rank': rank + 1
    }

    start_time = perf_counter()
    # projector.reset()
    # metric_dict = projector.project_wplus(
    #   outdir=outdir,
    #   image_path=image_path,
    #   distributed=distributed,
    #   lpips_metric=lpips_metric,
    #   **global_cfg.project_wplus_kwargs
    # )
    elapsed_time = (perf_counter() - start_time)
    if rank == 0:
      tqdm.tqdm.write(f'processing {image_path.stem} elapsed: {elapsed_time:.1f} s')

    metric_dict['elapsed_time_second'] = elapsed_time
    metric_dict['elapsed_time_minute'] = elapsed_time / 60
    with open(f"{outdir}/metrics.json", 'w') as f:
      json.dump(metric_dict, f, indent=2)

    # average value if distributed
    if distributed:
      metric_dict = ddp_utils.d2_reduce_dict(input_dict=metric_dict, average=True)
      ddp_utils.d2_synchronize()

    if rank == 0:
      if len(avg_recorder_dict) == 0:
        for k in metric_dict.keys():
          avg_recorder_dict[k] = AverageMeter()
      for k in metric_dict.keys():
        avg_recorder_dict[k].update(metric_dict[k])

      summary_dict = {}
      loss_str = ""
      for k in avg_recorder_dict.keys():
        v_avg = avg_recorder_dict[k].avg
        summary_dict[k] = v_avg
        loss_str += f'{k}: {v_avg:.4g}, '
      tqdm.tqdm.write(loss_str)
      summary_dict2txtfig(summary_dict, prefix='eval', step=idx, textlogger=global_textlogger, save_fig_sec=30)

    if idx % 20 == 0 and rank == 0:
      modelarts_utils.modelarts_sync_results_dir(cfg=global_cfg, join=False)

    if distributed: ddp_utils.d2_synchronize()

    if global_cfg.tl_debug:
      break

  if is_main_process:
    modelarts_utils.prepare_dataset(global_cfg.get('modelarts_upload', {}), global_cfg=global_cfg, download=False)
    modelarts_utils.modelarts_sync_results_dir(global_cfg, join=True)
  if distributed: ddp_utils.d2_synchronize()
  pass





if __name__ == '__main__':
  main()
