import traceback
import pprint
import logging
import os
import argparse
import random
import numpy as np
from einops import rearrange

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms.functional as tv_f
from torchvision.datasets import ImageFolder as ImageFolder_base

from tl2.proj.fvcore.checkpoint import Checkpointer

from .ddp.ddp_utils import parser_local_rank, is_distributed


def init_seeds(seed=0,
               rank=0,
               # cuda_deterministic=True
               ):
  seed = seed + rank
  print(f"{rank}: seed={seed}")

  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)

  if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

  # if cuda_deterministic:
  #   torch.backends.cudnn.deterministic = True
  #   torch.backends.cudnn.benchmark = False
  # else:  # faster, less reproducible
  #   torch.backends.cudnn.deterministic = False
  #   torch.backends.cudnn.benchmark = True
  pass


def requires_grad(model, flag=True):
  for p in model.parameters():
    p.requires_grad = flag


def print_number_params(models_dict,
                        logger=None,
                        add_info=""):
  """
    self.module_name_list = []
    logger = logging.getLogger('tl')
    models_dict = {}
    for name in self.module_name_list:
      models_dict[name] = getattr(self, name)
    models_dict['G'] = self
    torch_utils.print_number_params(models_dict=models_dict, logger=logger)
    logger.info(self)

  :param models_dict:
  :param logger:
  :param add_info:
  :return:
  """
  print()
  if logger is None:
    logger = logging.getLogger('tl')
    print_func = logger.info
  elif hasattr(logger, 'info'):
    print_func = logger.info
  else:
    print_func = logger

  for label, model in models_dict.items():
    if model is None:
      # logger.info(f'Number of params in {label}:\t 0M')
      print_func(f'{label + ":":<40} '
                 f"{'paras:'} {0:10.6f}M  {add_info}")
    else:
      num_params = sum([p.data.nelement() for p in model.parameters()]) / 1e6
      num_bufs = sum([p.data.nelement() for p in model.buffers()]) / 1e6

      print_func(f'{label + ":":<40} '
                 f"{'paras:'} {num_params:10.6f}M"
                 f"{'':<1} bufs: {str(num_bufs)}M  {add_info}",
                 )

def save_models(save_dir,
                model_dict,
                info_msg=None,
                cfg=None,
                msg_mode='w'):
  """
  def save_models(
      unet,
      state_dict,
      info_msg,
      saved_dir=None):

    model_dict = {
        'unet': unet,
    }

    if saved_dir is None:
        ckpt_max2keep = tl2_utils.MaxToKeep.get_named_max_to_keep(name='ckpt', use_circle_number=True)
        saved_dir = ckpt_max2keep.step_and_ret_circle_dir(global_cfg.tl_ckptdir)
    os.makedirs(saved_dir, exist_ok=True)

    global_cfg.dump_to_file_with_command(f"{saved_dir}/config_command.yaml", global_cfg.tl_command)

    torch_utils.save_models(save_dir=saved_dir, model_dict=model_dict)
    tl2_utils.write_info_msg(saved_dir, info_msg)

    return saved_dir

  Args:
    save_dir:
    model_dict:
    info_msg:
    cfg:
    msg_mode:

  Returns:

  """
  os.makedirs(save_dir, exist_ok=True)
  for name, model in model_dict.items():
    if hasattr(model, 'state_dict'):
      # module and optim
      torch.save(model.state_dict(), f"{save_dir}/{name}.pth")
      if isinstance(model, nn.Module):
        torch.save(model, f"{save_dir}/{name}_model.pth")
    else:
      # dict
      torch.save(model, f"{save_dir}/{name}.pth")

  if info_msg is not None:
    with open(f"{save_dir}/0info.txt", msg_mode) as f:
      f.write(f"{info_msg}\n")

  if cfg is not None:
    cfg.dump_to_file_with_command(f"{save_dir}/config_command.yaml", cfg.tl_command)

  pass

def load_models(save_dir,
                model_dict,
                rank=0,
                verbose=True,
                **kwargs):
  logger = logging.getLogger('tl')
  logger.info(f"Loading models from {save_dir}\n"
              f"models: {model_dict.keys()}")

  map_location = lambda storage, loc: storage.cuda(rank)

  for name, model in model_dict.items():
    ckpt_path = f"{save_dir}/{name}.pth"
    if not os.path.exists(ckpt_path):
      logger.info(f"Do not exist, skip load {ckpt_path}!")
      continue
    # if isinstance(model, torch.nn.Module):
    #   model_ckpt = Checkpointer(model=model)
    #   model_ckpt.load_state_dict_from_file(ckpt_path)
    #   del model_ckpt
    #   torch.cuda.empty_cache()
    if hasattr(model, 'load_state_dict'):
      logger.info(f"Loading {name:<40}: load_state_dict")
      loaded_state = torch.load(ckpt_path, map_location=map_location)
      if isinstance(model, nn.Module):
        if verbose:
          model_ckpt = Checkpointer(model=model)
          model_ckpt.load_state_dict(loaded_state)
          del model_ckpt
        else:
          ret = model.load_state_dict(loaded_state, strict=False)
          logger.info(pprint.pformat(ret))

      elif isinstance(model, optim.Optimizer):
        try:
          ret = model.load_state_dict(loaded_state)
        except:
          logger.info(traceback.format_exc())
      else:
        ret = model.load_state_dict(loaded_state)
      del loaded_state
      torch.cuda.empty_cache()
    else:
      logger.info(f"Loading {name:<40}: update")
      loaded_state = torch.load(ckpt_path, map_location=map_location)
      model.update(loaded_state)
      del loaded_state
      torch.cuda.empty_cache()
  pass

def torch_load(model_path, rank):
  map_location = lambda storage, loc: storage.cuda(rank)
  loaded_model = torch.load(model_path, map_location=map_location)
  logging.getLogger('tl').info(f"Load model: {model_path}")
  return loaded_model


def set_optimizer_lr(optimizer,
                     lr):
  for param_group in optimizer.param_groups:
    param_group['lr'] = lr
  pass

def mul_optimizer_lr(optimizer,
                     lr_mul):
  for param_group in optimizer.param_groups:
    param_group['lr'] = param_group['initial_lr'] * lr_mul
  pass


def get_optimizer_lr(optimizer,
                     return_all=True):
  lr = []
  for param_group in optimizer.param_groups:
    lr.append(param_group['lr'])
    if not return_all:
      break
  if len(lr) == 1:
    return lr[0]
  else:
    return lr


def select_indices(bs,
                   dim,
                   device,
                   num_samples,
                   replacement=False):

  select_inds = torch.multinomial(torch.ones(*[bs, dim], device=device),
                                  num_samples=num_samples, replacement=replacement)
  return select_inds


def batch_random_split_indices(
      bs,
      num_points,
      grad_points,
      device
):
  rand_idx_list = []
  for i in range(bs):
    rand_idx = torch.randperm(num_points, device=device)
    rand_idx_list.append(rand_idx)

  batch_rand_idx = torch.stack(rand_idx_list, dim=0)

  idx_grad = batch_rand_idx[:, 0:grad_points]
  idx_no_grad = batch_rand_idx[:, grad_points:]

  return idx_grad, idx_no_grad

def batch_gather_points(points,
                        idx_grad):
  """

  :param points: (b, n, c) or (b, n, s, c)
  :param idx_grad: (b, Ngrad)
  :return:
  """
  if points.dim() == 4:
    idx_grad = rearrange(idx_grad, "b n -> b n 1 1")
    idx_grad = idx_grad.expand(points.shape[0], -1, points.shape[-2], points.shape[-1])
    sampled_points = torch.gather(points, dim=1, index=idx_grad, sparse_grad=False)
  elif points.dim() == 3:
    idx_grad = rearrange(idx_grad, "b n -> b n 1")
    idx_grad = idx_grad.expand(points.shape[0], -1, points.shape[-1])
    sampled_points = torch.gather(points, dim=1, index=idx_grad, sparse_grad=False)
  else:
    assert 0
  return sampled_points


def gather_points(points,
                  sample_idx,
                  dim):
  """

  :param points: (b c h w)
  :param idx_grad: (b, n)
  :return:
  """

  rearrange_shape = ['1'] * len(points.shape)
  rearrange_shape[0] = 'b'
  rearrange_shape[dim] = 'n'
  rearrange_shape_str = ' '.join(rearrange_shape)

  expand_shape = list(points.shape)
  expand_shape[dim] = -1

  sample_idx = rearrange(sample_idx, f"b n -> {rearrange_shape_str}")
  sample_idx = sample_idx.expand(*expand_shape)
  sampled_points = torch.gather(points, dim=dim, index=sample_idx, sparse_grad=False)

  return sampled_points


def batch_scatter_points(idx_grad,
                         points_grad,
                         idx_no_grad,
                         points_no_grad,
                         dim):
  """

  :param idx_grad: (b, Ngrad)
  :param points_grad: (b, N) or (b, N, c)
  :param idx_no_grad:
  :param points_no_grad:
  :param num_points:
  :return:
  """

  output_shape = list(points_grad.shape)
  output_shape[dim] += points_no_grad.shape[dim]

  points_all = torch.zeros(*output_shape, device=points_grad.device, dtype=points_grad.dtype)

  rearrange_shape = ['1'] * len(output_shape)
  rearrange_shape[0] = 'b'
  rearrange_shape[dim] = 'n'
  rearrange_shape_str = ' '.join(rearrange_shape)

  expand_shape = output_shape
  expand_shape[dim] = -1

  idx_grad = rearrange(idx_grad, f"b n -> {rearrange_shape_str}")
  idx_grad_out = idx_grad.expand(*expand_shape)
  points_all.scatter_(dim=dim, index=idx_grad_out, src=points_grad)

  idx_no_grad = rearrange(idx_no_grad, f"b n -> {rearrange_shape_str}")
  idx_no_grad_out = idx_no_grad.expand(expand_shape)
  points_all.scatter_(dim=dim, index=idx_no_grad_out, src=points_no_grad)

  return points_all

def get_grad_norm_string(named_params,
                         norm_type=2):

  named_params = list(named_params)

  parameters = [p for p in named_params if p[1].grad is not None]
  norm_type = float(norm_type)

  ret_str = ""
  for name, p in parameters:
    param_norm = torch.norm(p.grad.detach(), p=norm_type)
    ret_str += f"{name}: {param_norm}\n"

  return ret_str


def get_grad_norm_total(params,
                        norm_type=2):
  """

  :param params:
  :param norm_type:
  :return:
  """

  params = list(params)

  parameters = [p for p in params if p.grad is not None]

  if len(parameters) == 0:
    return -1

  norm_type = float(norm_type)
  device = parameters[0].grad.device

  total_norm = torch.norm(torch.stack([torch.norm(p.grad.detach(), norm_type).to(device) for p in parameters]),
                          norm_type).item()

  return total_norm


def img_clamp_norm(img,
                   low,
                   high,
                   mean0=False):
  """

  :param img:
  :param low:
  :param high:
  :return

  - img_tensor: [0, 1]

  """
  img = img.clone()
  img.clamp_(min=low, max=high)
  img.sub_(low).div_(max(high - low, 1e-5))
  if mean0:
    img = img * 2. - 1
  return img


def img_tensor_to_pil(frame_tensor,
                      low=-1,
                      high=1,
                      ):
  frame_tensor = frame_tensor.squeeze()
  frame_tensor = img_clamp_norm(frame_tensor, low=low, high=high)
  img_pil = tv_f.to_pil_image(frame_tensor)
  return img_pil


class ImageFolder(ImageFolder_base):
  def __init__(self, *args, **kwargs):
    """A generic data loader where the images are arranged in this way by default: ::

        root/dog/xxx.png
        root/dog/xxy.png
        root/dog/[...]/xxz.png

        root/cat/123.png
        root/cat/nsdf3.png
        root/cat/[...]/asd932_.png

    This class inherits from :class:`~torchvision.datasets.DatasetFolder` so
    the same methods can be overridden to customize the dataset.

    Args:
        root (string): Root directory path.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        loader (callable, optional): A function to load an image given its path.
        is_valid_file (callable, optional): A function that takes path of an Image file
            and check if the file is a valid file (used to check of corrupt files)

     Attributes:
        classes (list): List of the class names sorted alphabetically.
        class_to_idx (dict): Dict with items (class_name, class_index).
        imgs (list): List of (image path, class_index) tuples
    """
    super(ImageFolder, self).__init__(*args, **kwargs)
    pass

  def sample_partial_samples(self, N_samples):
    self.samples = self.samples[:N_samples]
    self.targets = [s[1] for s in self.samples]
    self.imgs = self.samples
    pass


def ema_accumulate(model1,
                   model2,
                   decay=0.999):
  """
  Exponential moving average for generator weights

  :param model1:
  :param model2:
  :param decay:
  :return:
  """
  if isinstance(model1, nn.Module):
    par1 = dict(model1.state_dict())
  else:
    par1 = model1

  if isinstance(model2, nn.Module):
    par2 = dict(model2.state_dict())
  else:
    par2 = model2

  with torch.no_grad():
    for k in par1.keys():
      par1[k].data.mul_(decay).add_(par2[k].data, alpha=1 - decay)


def get_gather_sample_idx(batch,
                          N_size,
                          N_samples,
                          device):
  window_size = N_size // N_samples

  base_idx = torch.arange(N_samples, device=device, dtype=torch.int64) * window_size
  base_idx = base_idx.unsqueeze(0).repeat([batch, 1])

  shift_idx = torch.randint_like(base_idx, window_size)
  sample_idx = base_idx + shift_idx

  return sample_idx

def sample_image_sub_pixels(images,
                            N_h_pixels,
                            N_w_pixels,
                            device,
                            sample_idx_h=None,
                            sample_idx_w=None):
  B, C, H, W = images.shape

  if sample_idx_h is None:
    sample_idx_h = get_gather_sample_idx(batch=B, N_size=H, N_samples=N_h_pixels, device=device)
  image_h = gather_points(points=images, sample_idx=sample_idx_h, dim=2)

  if sample_idx_w is None:
    sample_idx_w = get_gather_sample_idx(batch=B, N_size=W, N_samples=N_w_pixels, device=device)
  image_hw = gather_points(points=image_h, sample_idx=sample_idx_w, dim=3)

  return image_hw


def get_gather_sample_idx_patch(batch,
                                all_size,
                                patch_size,
                                device):

  shift_idx = torch.arange(patch_size, device=device, dtype=torch.int64)
  shift_idx = shift_idx.unsqueeze(0).repeat([batch, 1])

  base_idx = torch.randint(0, all_size - patch_size + 1, [batch, 1], device=device)
  sample_idx = base_idx + shift_idx

  return sample_idx

def sample_image_patch(images,
                       patch_size_h,
                       patch_size_w,
                       device,
                       sample_idx_h=None,
                       sample_idx_w=None):
  B, C, H, W = images.shape

  if sample_idx_h is None:
    sample_idx_h = get_gather_sample_idx_patch(batch=B, all_size=H, patch_size=patch_size_h, device=device)
  image_h = gather_points(points=images, sample_idx=sample_idx_h, dim=2)

  if sample_idx_w is None:
    sample_idx_w = get_gather_sample_idx_patch(batch=B, all_size=W, patch_size=patch_size_w, device=device)
  image_hw = gather_points(points=image_h, sample_idx=sample_idx_w, dim=3)

  return image_hw


def sample_noises(bs,
                  noise_dim,
                  device,
                  N_samples=1,
                  seed=None):
  if seed is not None:
    z_samples = np.random.RandomState(seed).randn(N_samples, bs, noise_dim)
    z_samples = torch.from_numpy(z_samples).to(device).to(torch.float32)

  else:
    z_samples = torch.randn(N_samples, bs, noise_dim, device=device)

  z_samples = z_samples.unbind(dim=0)

  return z_samples
