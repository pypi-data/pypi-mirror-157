import collections
import shutil
import traceback
import pprint
import logging
import argparse
import os
import numpy as np
import math
from tqdm import tqdm
import copy

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parallel import DistributedDataParallel as DDP
from torchvision.utils import save_image, make_grid
import torchvision.transforms.functional as trans_f

from tl2.launch.launch_utils import update_parser_defaults_from_yaml, global_cfg
from tl2.modelarts import modelarts_utils
from tl2.proj.fvcore import build_model
from tl2.proj.logger.textlogger import summary_dict2txtfig, summary_defaultdict2txtfig, global_textlogger
from tl2 import tl2_utils
from tl2.proj.pytorch import torch_utils
from tl2.proj.pytorch.ddp import ddp_utils
from tl2.proj.argparser import argparser_utils
from tl2.proj.pytorch.examples.gan_ddp import comm_utils
from tl2.proj.pytorch.examples.gan_ddp import datasets
from tl2.proj.pytorch.examples.gan_ddp import diff_aug

from torch_fidelity import calculate_metrics


def setup_ddp(rank, world_size, port):
  os.environ['MASTER_ADDR'] = 'localhost'
  os.environ['MASTER_PORT'] = port

  # initialize the process group
  # dist.init_process_group("gloo", rank=rank, world_size=world_size)
  dist.init_process_group("nccl", rank=rank, world_size=world_size)
  dist.barrier()
  pass

def cleanup():
  dist.destroy_process_group()


def to_range01(img):
  """

  :param img: [-1, 1]
  :return:
  """
  img = (img + 1) * 0.5
  return img


def build_model_and_resume(
      resume_dir,
      rank,
      logger,
      device):
  state_dict = {
    'best_fid': np.inf,
    'iters': 0,
    'epochs': 0,
  }
  generator = build_model(cfg=global_cfg.G_cfg).to(device)
  discriminator = build_model(cfg=global_cfg.D_cfg).to(device)
  G_ema = copy.deepcopy(generator)
  ema_model = comm_utils.EMA(
    source=generator, target=G_ema, decay=global_cfg.ema_decay, start_itr=global_cfg.ema_start_itr)

  if global_cfg.tl_resume:
    model_dict = {
      'generator': generator,
      'discriminator': discriminator,
      'state_dict': state_dict,
    }
    if global_cfg.load_G_ema:
      model_dict['G_ema'] = G_ema
    torch_utils.load_models(save_dir=resume_dir, model_dict=model_dict, strict=False, rank=rank)
    if global_cfg.load_G_ema:
      ema_model.update_target_dict(G_ema.state_dict())
    else:
      ema_model.update_target_dict(generator.state_dict())

    if global_cfg.reset_best_fid:
      state_dict['best_fid'] = np.inf
    logger.info(pprint.pformat(state_dict))

  return generator, discriminator, G_ema, ema_model, state_dict


def build_optimizer(G, D):

  optimizer_G = torch.optim.Adam(
    params=[{'params': G.parameters(),
             'initial_lr': global_cfg.gen_lr}],
    lr=global_cfg.gen_lr,
    betas=global_cfg.betas,
    weight_decay=0)
  optimizer_D = torch.optim.Adam(
    params=[{'params': D.parameters(),
             'initial_lr': global_cfg.disc_lr}],
    lr=global_cfg.disc_lr,
    betas=global_cfg.betas,
    weight_decay=0)

  return optimizer_G, optimizer_D

def build_optimizer_and_resume(generator_ddp,
                               discriminator_ddp,
                               resume_dir,
                               rank):
  optimizer_G, optimizer_D = build_optimizer(G=generator_ddp, D=discriminator_ddp)

  scaler_G = torch.cuda.amp.GradScaler(enabled=global_cfg.use_amp_G)
  scaler_D = torch.cuda.amp.GradScaler(enabled=global_cfg.use_amp_D)

  if global_cfg.tl_resume and global_cfg.load_optimizers:
    model_dict = {
      'optimizer_G': optimizer_G,
      'optimizer_D': optimizer_D,
      'scaler_G': scaler_G,
      'scaler_D': scaler_D,
    }
    torch_utils.load_models(save_dir=resume_dir, model_dict=model_dict, strict=False, rank=rank)

    optimizer_G.param_groups[0]['lr'] = global_cfg.gen_lr
    optimizer_D.param_groups[0]['lr'] = global_cfg.disc_lr

  return optimizer_G, optimizer_D, scaler_G, scaler_D


def setup_eval_dataset(dataset,
                       saved_dir,
                       num_imgs,
                       del_fid_real_images,
                       world_size,
                       rank,
                       batch_size=100):

  if del_fid_real_images and rank == 0:
    shutil.rmtree(saved_dir, ignore_errors=True)

  # Only make real images if they haven't been made yet
  logger = logging.getLogger('tl')

  # important
  ddp_utils.d2_synchronize()

  if not os.path.exists(saved_dir):
    if rank == 0:
      os.makedirs(saved_dir, exist_ok=True)
      pbar = tqdm(total=num_imgs, desc=f"Outputting real images for eval: {saved_dir}")

    ddp_utils.d2_synchronize()

    dataloader, sampler = datasets.get_dataloader_distributed(
      dataset=dataset,
      batch_size=batch_size,
      world_size=world_size,
      rank=rank,
      num_workers=0,
      shuffle=False,
      drop_last=False
    )
    count = 0
    for idx, (imgs, _) in enumerate(dataloader):
      if count >= num_imgs:
        break
      if rank == 0:
        pbar.update(world_size * batch_size)

      # img = (img.squeeze() + 1) * 0.5
      imgs = to_range01(img=imgs)

      for sub_idx, img in enumerate(imgs):
        img_pil = trans_f.to_pil_image(img)

        number = idx * world_size * batch_size + rank * batch_size + sub_idx
        img_pil.save(f"{saved_dir}/{number:06d}.png")
      count += world_size * batch_size
  else:
    logger.info("Real images exist.")

  ddp_utils.d2_synchronize()
  pass


def setup_gen_images(generator,
                     rank,
                     world_size,
                     fake_dir,
                     num_imgs=2048,
                     img_size=128):
  if rank == 0:
    shutil.rmtree(fake_dir, ignore_errors=True)
    os.makedirs(fake_dir, exist_ok=True)

  ddp_utils.d2_synchronize()

  generator.eval()

  if rank == 0:
    pbar = tqdm(desc=f"Generating images at {img_size}x{img_size} {fake_dir}", total=num_imgs)

  with torch.no_grad():
    img_counter = 0
    count = 0
    while img_counter < num_imgs:
      if rank == 0:
        pbar.update(world_size)

      zs = generator.get_zs(1)
      img = generator(zs)

      # img = (img.squeeze() + 1.) * 0.5
      img = to_range01(img=img.squeeze())
      img_pil = trans_f.to_pil_image(img)

      number = count * world_size + rank
      img_pil.save(f"{fake_dir}/{number:06d}.png")

      img_counter += world_size
      count += 1

  if rank == 0: pbar.close()

  ddp_utils.d2_synchronize()
  pass


def calculate_fid(real_dir,
                  fake_dir):

  metrics_dict = calculate_metrics(input1=real_dir,
                                   input2=fake_dir,
                                   cuda=True,
                                   isc=False,
                                   fid=True,
                                   kid=False,
                                   verbose=False)
  fid = metrics_dict['frechet_inception_distance']

  # torch.cuda.empty_cache()

  return fid


def saved_models_and_images(G_ema,
                            generator,
                            discriminator,
                            optimizer_G,
                            optimizer_D,
                            scaler_G,
                            scaler_D,
                            state_dict,
                            fixed_z,
                            saved_dir=None,
                            metadata=None,
                            forward_bs=4,
                            info_msg=""):
  model_dict = {
    'G_ema': G_ema,
    'generator': generator,
    'discriminator': discriminator,
    'optimizer_G': optimizer_G,
    'optimizer_D': optimizer_D,
    'scaler_G': scaler_G,
    'scaler_D': scaler_D,
    'state_dict': state_dict,
  }

  info_msg = f"epoch: {state_dict['epochs']}\n" \
             f"step: {state_dict['iters']}\n" + info_msg
  if saved_dir is None:
    ckpt_max2keep = tl2_utils.MaxToKeep.get_named_max_to_keep(name='ckpt', max_to_keep=4, use_circle_number=True)
    saved_dir = ckpt_max2keep.step_and_ret_circle_dir(global_cfg.tl_ckptdir, info_msg=info_msg)

  os.makedirs(saved_dir, exist_ok=True)

  # save meta and global_cfg
  if metadata is not None:
    tl2_utils.json_dump(metadata, f"{saved_dir}/metadata.json")
  global_cfg.dump_to_file_with_command(f"{saved_dir}/config_command.yaml", global_cfg.tl_command)

  torch_utils.save_models(save_dir=saved_dir, model_dict=model_dict, info_msg=info_msg)

  save_images(G_ema=G_ema, fixed_z=fixed_z, saved_dir=f"{saved_dir}/imgs", forward_bs=forward_bs)
  torch.cuda.empty_cache()

  pass


@torch.no_grad()
def save_images(G_ema,
                fixed_z,
                saved_dir,
                forward_bs=4):
  os.makedirs(saved_dir, exist_ok=True)
  G_ema.eval()
  bs = len(fixed_z)

  num_iters = (bs + forward_bs - 1) // forward_bs

  with torch.cuda.amp.autocast(global_cfg.use_amp_G):
    imgs = []
    for idx in range(num_iters):
      z = fixed_z[idx * forward_bs : (idx + 1) * forward_bs]
      img = G_ema(z)
      imgs.append(img)

  imgs = torch.cat(imgs, dim=0)

  imgs = to_range01(img=imgs)

  save_image(imgs, f"{saved_dir}/G_ema_z.png", nrow=int(math.sqrt(bs)), normalize=False)
  pass


def main(rank,
         world_size,
         opt,
         ):
  if world_size > 1:
    setup_ddp(rank, world_size, opt.port)

  torch.cuda.set_device(rank)
  device = torch.device(rank)

  update_parser_defaults_from_yaml(parser=None, is_main_process=(rank == 0))
  if rank == 0 and opt.modelarts:
    modelarts_utils.setup_tl_outdir_obs(global_cfg, unzip_code=False)
    modelarts_utils.modelarts_sync_results_dir(global_cfg, join=True)
    modelarts_utils.prepare_dataset(global_cfg.get('modelarts_download', {}), global_cfg=global_cfg)

  logger = logging.getLogger('tl')
  torch_utils.init_seeds(seed=global_cfg.seed, rank=rank)

  resume_dir = f"{global_cfg.tl_resumedir}/ckptdir/resume"
  generator, discriminator, G_ema, ema_model, state_dict = build_model_and_resume(
    resume_dir=resume_dir, logger=logger, device=device, rank=rank)

  if world_size > 1:
    generator_ddp = DDP(generator, device_ids=[rank], find_unused_parameters=True, broadcast_buffers=False)
    discriminator_ddp = DDP(discriminator, device_ids=[rank], find_unused_parameters=True, broadcast_buffers=False)
    generator = generator_ddp.module
    discriminator = discriminator_ddp.module
  else:
    generator_ddp = generator
    discriminator_ddp = discriminator

  optimizer_G, optimizer_D, scaler_G, scaler_D = build_optimizer_and_resume(
    generator_ddp=generator_ddp, discriminator_ddp=discriminator_ddp, resume_dir=resume_dir, rank=rank)

  # ----------
  #  Training
  # ----------

  # dataset
  dataset = build_model(cfg=global_cfg.data_cfg)
  img, _ = dataset[0]
  image_size = img.shape[-1]
  dataloader, sampler = datasets.get_dataloader_distributed(
    dataset=dataset,
    batch_size=global_cfg.batch_size,
    world_size=world_size,
    rank=rank,
    num_workers=global_cfg.num_workers,
    shuffle=True,
  )
  assert global_cfg.batch_size % global_cfg.batch_split == 0

  fixed_z = generator.get_zs(global_cfg.fixed_z_bs)
  use_diffaug = global_cfg.use_diffaug
  dummy_tensor = torch.tensor([0], device=device)

  if rank == 0:
    num_iters = (len(dataset) // world_size + global_cfg.batch_size - 1) // global_cfg.batch_size
    pbar_iters = tqdm(total=num_iters)

  out_dict = collections.defaultdict(dict)
  # loop epochs
  while True:
    sampler.set_epoch(epoch=state_dict['epochs'])
    if rank == 0:
      pbar_iters.reset()

    for i, (imgs, _) in enumerate(dataloader):

      ddp_utils.d2_synchronize()

      out_dict.clear()
      out_dict['epoch']['epoch'] = state_dict['epochs']
      out_dict['iter']['iter'] = state_dict['iters']

      generator_ddp.train()
      discriminator_ddp.train()

      real_imgs = imgs.to(device, non_blocking=True)
      cur_bs = real_imgs.shape[0]

      # TRAIN DISCRIMINATOR
      torch_utils.requires_grad(generator_ddp, False)
      torch_utils.requires_grad(discriminator_ddp, True)

      with torch.cuda.amp.autocast(global_cfg.use_amp_D):
        # Generate images for discriminator training
        with torch.no_grad():
          zs = generator.get_zs(cur_bs)
          split_batch_size = cur_bs // global_cfg.batch_split
          gen_imgs = []
          for split in range(global_cfg.batch_split):
            subset_z = zs[split * split_batch_size : (split+1) * split_batch_size]
            g_imgs = generator_ddp(subset_z)
            gen_imgs.append(g_imgs)

          gen_imgs = torch.cat(gen_imgs, axis=0)
          if use_diffaug:
            gen_imgs = diff_aug.DiffAugment(gen_imgs)

        # real_imgs.requires_grad = True
        if use_diffaug:
          real_imgs = diff_aug.DiffAugment(real_imgs)
        real_imgs.requires_grad_()
        d_real_logits = discriminator_ddp(real_imgs)

      d_regularize = i % global_cfg.d_reg_every == 0

      # Gradient penalty
      if global_cfg.r1_lambda > 0 and d_regularize:
        grad_real = torch.autograd.grad(
          outputs=scaler_D.scale(d_real_logits.sum()), inputs=real_imgs, create_graph=True)
        inv_scale = 1. / scaler_D.get_scale()
        grad_real = [p * inv_scale for p in grad_real][0]
      with torch.cuda.amp.autocast(global_cfg.use_amp_D):
        if global_cfg.r1_lambda > 0 and d_regularize:
          grad_penalty = (grad_real.view(grad_real.size(0), -1).norm(2, dim=1) ** 2).mean()
          grad_penalty = 0.5 * global_cfg.r1_lambda * global_cfg.d_reg_every * grad_penalty + 0 * d_real_logits[0]
        else:
          grad_penalty = dummy_tensor

        d_fake_logits = discriminator_ddp(gen_imgs)

        with torch.no_grad():
          D_real_logits = d_real_logits.mean().item()
          D_fake_logits = d_fake_logits.mean().item()
          out_dict['D_logits']['D_real_logits'] = D_real_logits
          out_dict['D_logits']['D_fake_logits'] = D_fake_logits

        D_real_logits_loss = torch.nn.functional.softplus(-d_real_logits).mean()
        D_fake_logits_loss = torch.nn.functional.softplus(d_fake_logits).mean()

        d_loss = D_real_logits_loss + D_fake_logits_loss + grad_penalty

        out_dict['D_logits_loss']['D_real_logits_loss'] = D_real_logits_loss.item()
        out_dict['D_logits_loss']['D_fake_logits_loss'] = D_fake_logits_loss.item()
        out_dict['grad_penalty']['grad_penalty'] = grad_penalty.item()
        out_dict['d_loss']['d_loss'] = d_loss.item()

      optimizer_D.zero_grad()
      scaler_D.scale(d_loss).backward()
      scaler_D.unscale_(optimizer_D)
      try:
        D_total_norm = torch.nn.utils.clip_grad_norm_(discriminator_ddp.parameters(), global_cfg.grad_clip,
                                                      # error_if_nonfinite=True, # torch >= 1.9
                                                      )
        out_dict['norm']['D_total_norm'] = D_total_norm.item()
      except:
        logger.info(traceback.format_exc())
        saved_models_and_images(G_ema=G_ema,
                                generator=generator,
                                discriminator=discriminator,
                                optimizer_G=optimizer_G,
                                optimizer_D=optimizer_D,
                                scaler_G=scaler_G,
                                scaler_D=scaler_D,
                                state_dict=state_dict,
                                fixed_z=fixed_z,
                                saved_dir=f"{global_cfg.tl_ckptdir}/D_crupted",
                                forward_bs=global_cfg.forward_bs)
        optimizer_D.zero_grad()
        D_total_norm = -1
        out_dict['norm']['D_total_norm'] = D_total_norm
        # exit(0)
      if D_total_norm > 0:
        scaler_D.step(optimizer_D)
      scaler_D.update()

      # TRAIN GENERATOR
      torch_utils.requires_grad(generator_ddp, True)
      torch_utils.requires_grad(discriminator_ddp, False)

      zs = generator.get_zs(cur_bs)
      split_batch_size = cur_bs // global_cfg.batch_split

      optimizer_G.zero_grad()
      for split in range(global_cfg.batch_split):
        with torch.cuda.amp.autocast(global_cfg.use_amp_G):
          subset_z = zs[split * split_batch_size : (split + 1) * split_batch_size]
          gen_imgs = generator_ddp(subset_z).to(torch.float32)
          if use_diffaug:
            gen_imgs = diff_aug.DiffAugment(gen_imgs)

        with torch.cuda.amp.autocast(global_cfg.use_amp_D):
          g_logits = discriminator_ddp(gen_imgs)

        if global_cfg.topk_v > 0:
          topk_percentage = 0.99 ** (state_dict['iters'] / global_cfg.topk_interval)
          topk_percentage = max(topk_percentage, global_cfg.topk_v)
          topk_num = math.ceil(topk_percentage * cur_bs)
          g_logits = torch.topk(g_logits, topk_num, dim=0).values
        else:
          topk_num = cur_bs

        G_fake_logits_loss = torch.nn.functional.softplus(-g_logits).mean()

        scaler_G.scale(G_fake_logits_loss).backward()

      scaler_G.unscale_(optimizer_G)

      with torch.no_grad():
        G_fake_logits = g_logits.mean().item()
        out_dict['D_logits']['G_fake_logits'] = G_fake_logits

      out_dict['D_logits_loss']['G_fake_logits_loss'] = G_fake_logits_loss.item()
      out_dict['topk_num']['topk_num'] = topk_num

      try:
        G_total_norm = torch.nn.utils.clip_grad_norm_(generator_ddp.parameters(), global_cfg.grad_clip,
                                                      # error_if_nonfinite=True, # torch >= 1.9
                                                      )
        out_dict['norm']['G_total_norm'] = G_total_norm.item()
      except:
        logger.info(traceback.format_exc())
        saved_models_and_images(G_ema=G_ema,
                                generator=generator,
                                discriminator=discriminator,
                                optimizer_G=optimizer_G,
                                optimizer_D=optimizer_D,
                                scaler_G=scaler_G,
                                scaler_D=scaler_D,
                                state_dict=state_dict,
                                fixed_z=fixed_z,
                                saved_dir=f"{global_cfg.tl_ckptdir}/G_crupted",
                                forward_bs=global_cfg.forward_bs)
        G_total_norm = -1
        out_dict['norm']['G_total_norm'] = G_total_norm
        optimizer_G.zero_grad()
        # exit(0)

      if G_total_norm > 0:
        scaler_G.step(optimizer_G)
      scaler_G.update()

      # update ema
      ema_model.update(itr=state_dict['iters'], source_dict=generator.state_dict())

      # log txt
      if rank == 0:
        out_dict['scalar']['scaler_G'] = scaler_G.get_scale()
        out_dict['scalar']['scaler_D'] = scaler_D.get_scale()
        out_dict['r1_lambda']['r1_lambda'] = global_cfg.r1_lambda
        out_dict['grad_clip']['grad_clip'] = global_cfg.grad_clip
        out_dict['batch_size']['batch_size'] = global_cfg.batch_size
        out_dict['lr']['gen_lr'] = optimizer_G.param_groups[0]['lr']
        out_dict['lr']['disc_lr'] = optimizer_D.param_groups[0]['lr']

        if i % global_cfg.print_every == 0:
          print_str = tl2_utils.get_print_dict_str(
            metric_dict=out_dict, float_format="+.6f", outdir=global_cfg.tl_outdir)
          tqdm.write(print_str)

        if (state_dict['iters'] % global_cfg.log_every == 0) and \
              state_dict['iters'] >= global_cfg.log_every_start or global_cfg.tl_debug:
          summary_defaultdict2txtfig(out_dict, prefix="train", step=state_dict['iters'], textlogger=global_textlogger)

      # eval ddp
      if state_dict['iters'] % global_cfg.save_every == 0 or global_cfg.tl_debug:
        eval_real_dir = f"{global_cfg.tl_outdir}/fid/real"
        eval_fake_dir = f"{global_cfg.tl_outdir}/fid/fake"
        # save real images
        setup_eval_dataset(dataset=dataset,
                           saved_dir=eval_real_dir,
                           num_imgs=global_cfg.num_images_real_eval,
                           del_fid_real_images=global_cfg.del_fid_real_images,
                           world_size=world_size,
                           rank=rank)
        global_cfg.del_fid_real_images = False
        ddp_utils.d2_synchronize()
        # save fake images
        setup_gen_images(generator=G_ema,
                         rank=rank,
                         world_size=world_size,
                         fake_dir=eval_fake_dir,
                         num_imgs=global_cfg.num_images_gen_eval,
                         img_size=image_size)
        ddp_utils.d2_synchronize()

        if rank == 0:
          # evaluation
          FID = calculate_fid(real_dir=eval_real_dir, fake_dir=eval_fake_dir)
          logger.info(f"\nepoch: {state_dict['epochs']}, step: {state_dict['iters']}, fid: {FID}\n")
          summary_dict = {
            'FID': FID
          }
          summary_dict2txtfig(summary_dict, prefix='eval', step=state_dict['iters'], textlogger=global_textlogger)

          # save best models
          if state_dict['best_fid'] > FID:
            state_dict['best_fid'] = FID
            saved_models_and_images(G_ema=G_ema,
                                    generator=generator,
                                    discriminator=discriminator,
                                    optimizer_G=optimizer_G,
                                    optimizer_D=optimizer_D,
                                    scaler_G=scaler_G,
                                    scaler_D=scaler_D,
                                    state_dict=state_dict,
                                    fixed_z=fixed_z,
                                    saved_dir=f"{global_cfg.tl_ckptdir}/best_fid",
                                    forward_bs=global_cfg.forward_bs,
                                    info_msg=f"FID: {FID}")

          # save models
          saved_models_and_images(G_ema=G_ema,
                                  generator=generator,
                                  discriminator=discriminator,
                                  optimizer_G=optimizer_G,
                                  optimizer_D=optimizer_D,
                                  scaler_G=scaler_G,
                                  scaler_D=scaler_D,
                                  state_dict=state_dict,
                                  fixed_z=fixed_z,
                                  forward_bs=global_cfg.forward_bs,
                                  info_msg=f"FID: {FID}")
          # save resume models
          saved_models_and_images(G_ema=G_ema,
                                  generator=generator,
                                  discriminator=discriminator,
                                  optimizer_G=optimizer_G,
                                  optimizer_D=optimizer_D,
                                  scaler_G=scaler_G,
                                  scaler_D=scaler_D,
                                  state_dict=state_dict,
                                  fixed_z=fixed_z,
                                  saved_dir=f"{global_cfg.tl_ckptdir}/resume",
                                  forward_bs=global_cfg.forward_bs,
                                  info_msg=f"FID: {FID}")
          if opt.modelarts:
            modelarts_utils.modelarts_sync_results_dir(cfg=global_cfg, join=False)

      # no blocking
      ddp_utils.d2_synchronize()
      state_dict['iters'] += 1
      if rank == 0:
        pbar_iters.update(1)
    state_dict['epochs'] += 1

  cleanup()
  pass


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--port', type=str, default='12355')
  argparser_utils.add_argument_bool(parser, 'modelarts', default=False)

  update_parser_defaults_from_yaml(parser)

  opt, _ = parser.parse_known_args()
  argparser_utils.print_args(opt)

  if opt.modelarts:
    modelarts_utils.setup_tl_outdir_obs(global_cfg, unzip_code=False)
    # modelarts_utils.modelarts_sync_results_dir(global_cfg, join=True)
    # modelarts_utils.prepare_dataset(global_cfg.get('modelarts_download', {}), global_cfg=global_cfg)

  num_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
  if num_gpus > 1:
    mp.spawn(main, args=(num_gpus, opt), nprocs=num_gpus, join=True)
  else:
    main(rank=0, world_size=num_gpus, opt=opt)

  if opt.modelarts:
    modelarts_utils.prepare_dataset(global_cfg.get('modelarts_upload', {}), global_cfg=global_cfg, download=False)
    modelarts_utils.modelarts_sync_results_dir(global_cfg, join=True)
