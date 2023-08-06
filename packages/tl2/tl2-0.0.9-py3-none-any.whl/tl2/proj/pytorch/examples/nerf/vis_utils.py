import numpy as np
from tqdm import tqdm

import torch

from tl2.proj.pil import pil_utils
from tl2.proj.cv2 import cv2_utils

# from models.volume_rendering import volume_render
from exp.comm.nerf import cam_params
from exp.comm.nerf.volume_rendering import volume_render


def get_rays_opencv_np(intrinsics: np.ndarray,
                       c2w: np.ndarray,
                       H: int,
                       W: int):
  '''
  ray batch sampling
      < opencv / colmap convention, standard pinhole camera >
      the camera is facing [+z] direction, x right, y downwards
                  z
                 ↗
                /
               /
              o------> x
              |
              |
              |
              ↓
              y

  :param H: image height
  :param W: image width
  :param intrinsics: [3, 3] or [4,4] intrinsic matrix
  :param c2w: [...,4,4] or [...,3,4] camera to world extrinsic matrix
  :return:
  '''
  prefix = c2w.shape[:-2]  # [...]

  # [H, W]
  u, v = np.meshgrid(np.arange(W), np.arange(H))
  # [H*W]
  u = u.reshape(-1).astype(dtype=np.float32) + 0.5  # add half pixel
  v = v.reshape(-1).astype(dtype=np.float32) + 0.5

  # [3, H*W]
  pixels = np.stack((u, v, np.ones_like(u)), axis=0)

  # [3, H*W]
  rays_d = np.matmul(np.linalg.inv(intrinsics[:3, :3]), pixels)

  # [..., 3, H*W] = [..., 3, 3] @ [1,1,...,  3, H*W], with broadcasting
  rays_d = np.matmul(c2w[..., :3, :3], rays_d.reshape([*len(prefix) * [1], 3, H * W]))
  # [..., H*W, 3]
  rays_d = np.moveaxis(rays_d, -1, -2)

  # [..., 1, 3] -> [..., H*W, 3]
  rays_o = np.tile(c2w[..., None, :3, 3], [*len(prefix) * [1], H * W, 1])

  return rays_o, rays_d


def to_img(tensor,
           H,
           W,
           imgscale):
  tensor = tensor.reshape(tensor.shape[0], H, W, -1).data.cpu().numpy()
  if imgscale:
    return (255 * np.clip(tensor, 0, 1)).astype(np.uint8)
  else:
    return tensor


def render_chunk(c2w,
                 intr,
                 H,
                 W,
                 device,
                 render_kwargs,
                 imgscale,
                 near,
                 far):
  # rays_o, rays_d = get_rays_opencv_np(intr, c2w, H, W)
  # rays_o = torch.from_numpy(rays_o).float().to(device)
  # rays_d = torch.from_numpy(rays_d).float().to(device)

  intr = torch.from_numpy(intr).to(device)
  c2w = torch.from_numpy(c2w).to(device)
  rays_o, rays_d, _ = cam_params.get_rays_by_intr_and_extr(intrinsics=intr, c2w=c2w, H=H, W=W)


  with torch.no_grad():
    rgb, depth, _ = volume_render(
      rays_o=rays_o,
      rays_d=rays_d,
      detailed_output=False,  # to return acc map and disp map
      show_progress=True,
      **render_kwargs)
  if imgscale:
    depth = (depth - near) / (far - near)

  rgb_img = to_img(rgb, H=H, W=W, imgscale=imgscale)
  depth_img = to_img(depth, H=H, W=W, imgscale=imgscale)

  return rgb_img, depth_img


def render_full(intr: np.ndarray,
                c2w: np.ndarray,
                H,
                W,
                near,
                far,
                render_kwargs,
                scene_model,
                device="cuda",
                batch_size=1,
                imgscale=True,
                outdir=None,
                debug=False):

  scene_model.to(device)

  if len(c2w.shape) == 2:
    c2w = c2w[None, ...]
  render_kwargs['batched'] = True

  if outdir is not None:
      video_f = cv2_utils.ImageioVideoWriter(f"{outdir}/render.mp4", fps=20, hd_video=True)

  for i in tqdm(range(0, c2w.shape[0], batch_size), desc="=> Rendering..."):
    rgb_i, depth_i = render_chunk(c2w=c2w[i:i + batch_size],
                                  intr=intr,
                                  H=H,
                                  W=W,
                                  device=device,
                                  render_kwargs=render_kwargs,
                                  imgscale=imgscale,
                                  near=near,
                                  far=far)
    for rgb, depth in zip(rgb_i, depth_i):
      rgb_pil = pil_utils.np_to_pil(rgb, )
      depth_pil = pil_utils.np_to_pil(depth.squeeze(), )
      merged_pil = pil_utils.merge_image_pil([rgb_pil, depth_pil], nrow=2, pad=1)
      if outdir is not None:
        video_f.write(merged_pil)
      if debug:
        pil_utils.imshow_pil(merged_pil, title=f"{rgb_pil.size}")


  if outdir is not None:
    video_f.release()
  pass
