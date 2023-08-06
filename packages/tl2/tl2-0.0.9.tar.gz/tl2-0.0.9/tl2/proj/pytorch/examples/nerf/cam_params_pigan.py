import utils
import numpy as np
from typing import Tuple
import matplotlib.pyplot as plt
from einops import rearrange

import torch
import torch.nn as nn
import torch.nn.functional as F

from pytorch3d import transforms as tr3d
from . import geometry_tensor


def _get_mesh_xy(H,
                 W,
                 device,
                 prefix_dims=[] # broadcast for batch
                 ):
  """

  :param H:
  :param W:
  :param device:
  :param prefix_dims:
  :return:
  - x: (b, HxW)
  - y: (b, HxW)
  """
  y, x = torch.meshgrid(torch.linspace(H * 3/2, H * (-1/2), H, device=device),
                        torch.linspace(W * (-1/2), W * 3/2, W, device=device))

  x = x.reshape([*[1] * len(prefix_dims), H * W]).expand([*prefix_dims, H * W])
  y = y.reshape([*[1] * len(prefix_dims), H * W]).expand([*prefix_dims, H * W])

  return x, y

def _get_mesh_xy_deprecated(H,
                            W,
                            device,
                            prefix_dims=[] # broadcast for batch
                            ):
  i, j = torch.meshgrid(torch.linspace(0, W - 1, W, device=device), torch.linspace(0, H - 1, H, device=device))
  i = i.t().reshape([*len(prefix_dims) * [1], H * W]).expand([*prefix_dims, H * W])
  j = j.t().reshape([*len(prefix_dims) * [1], H * W]).expand([*prefix_dims, H * W])

  return i, j


def _select_pixels(x,
                   y,
                   H,
                   W,
                   device,
                   N_rays=-1,
                   prefix_dims=[]):

  if N_rays > 0 and N_rays < H * W:
    select_inds = torch.multinomial(torch.ones(*[*prefix_dims, H*W], device=device),
                                    num_samples=N_rays, replacement=False)
    # select_inds = torch.from_numpy(
    #   np.random.choice(H * W, size=[*prefix_dims, N_rays], replace=False)
    # ).to(device)

    x = torch.gather(x, dim=-1, index=select_inds)
    y = torch.gather(y, dim=-1, index=select_inds)
  else:
    select_inds = torch.arange(H * W).to(device)
    if len(prefix_dims) > 0:
      select_inds = select_inds[None,].expand([*prefix_dims, -1])

  return x, y, select_inds


def _get_direction(H,
                   W,
                   focal_x,
                   focal_y,
                   prefix_dims,
                   device,
                   N_rays=-1,
                   center_x=None,
                   center_y=None,
                   normalize_rays_d=False):
  """

  :param H:
  :param W:
  :param focal_x:
  :param focal_y:
  :param prefix_dims: [b, ]
  :param device:
  :param N_rays:
  :return:
  """
  # [b, HxW]
  x, y = _get_mesh_xy(H=H, W=W, device=device, prefix_dims=prefix_dims)
  # x, y = _get_mesh_xy_deprecated(H=H, W=W, device=device, prefix_dims=prefix)
  # assert (i == x).all()
  # assert (j == y).all()

  # [b, N_rays], pixel coordinate
  x, y, select_inds = _select_pixels(x=x, y=y, H=H, W=W, N_rays=N_rays, device=device, prefix_dims=prefix_dims)

  if center_x is None:
    center_x = W / 2.
  if center_y is None:
    center_y = H / 2.

  # [..., N_rays, 3], axes orientations : x right, y downwards, z positive, pixel coordinate to camera coordinate
  dirs = torch.stack([(x - center_x) / focal_x,
                      (y - center_y) / focal_y,
                      - torch.ones_like(x, device=device)], dim=-1)

  if normalize_rays_d:
    dirs = torch.nn.functional.normalize(dirs, dim=-1)
  return dirs, select_inds


def get_rays(
      rot: torch.Tensor,
      trans: torch.Tensor,
      focal_x: torch.Tensor,
      focal_y: torch.Tensor,
      H: int,
      W: int,
      N_rays: int = -1,
      representation='axis-angle', # 'quaternion'
      flatten=True,
      **kwargs):
  """
  < opencv / colmap convention, standard pinhole camera >
    the camera is facing [+z] direction, x right, y downwards
                  z
                ↗
              o------> x
              ↓
              y
  :param rot: (b, 3)
  :param trans: (b, 3)
  :param focal_x: ()
  :param focal_y: ()
  :param H:
  :param W:
  :param N_rays: -1: all
  :param representation:

  :return

  - rays_o: (b, N_rays, 3)
  - rays_d: (b, N_rays, 3)
  - select_inds: (b, N_rays)
  """

  device = rot.device
  assert rot.shape[:-1] == trans.shape[:-1]
  prefix = rot.shape[:-1]  # [b, ]

  dirs, select_inds = _get_direction(H=H, W=W, focal_x=focal_x, focal_y=focal_y,
                                     prefix_dims=prefix, device=device, N_rays=N_rays)

  # ---------
  # Translate camera frame's origin to the world frame. It is the origin of all rays.
  # ---------

  if representation == 'quaternion':
    # rot: [..., 4], trans: [..., 3]
    assert rot.shape[-1] == 4
    quat = tr3d.standardize_quaternion(F.normalize(rot, dim=-1))
    rays_d = tr3d.quaternion_apply(quat[..., None, :], dirs)
    rays_o = trans[..., None, :].expand_as(rays_d)

  elif representation == 'axis-angle':
    # original paper, rot: [..., 3], trans: [..., 3]
    assert rot.shape[-1] == 3
    ## pytorch 3d implementation: axis-angle --> quaternion -->matrix, [..., 3, 3]
    rot_m = tr3d.axis_angle_to_matrix(rot)
    # rotation: matrix multiplication, [..., N_rays, 1, 3] * [..., 1, 3, 3]
    rays_d = torch.sum(dirs[..., None, :] * rot_m[..., None, :3, :3], dim=-1)
    rays_o = trans[..., None, :].expand_as(rays_d)

  elif representation == 'rotation6D':
    assert rot.shape[-1] == 6
    rot_m = tr3d.rotation_6d_to_matrix(rot)
    # rotation: matrix multiplication
    # rays_d = rot_m.view(*prefix, 1, 3, 3)\
    #     .expand([*prefix, N_rays, 3, 3]).flatten(0,-3).bmm(
    #     dirs.flatten(0, -2).view([-1, 3, 1]))
    # [..., N_rays, 1, 3] * [..., 1, 3, 3]
    rays_d = torch.sum(dirs[..., None, :] * rot_m[..., None, :3, :3], dim=-1)
    rays_o = trans[..., None, :].expand_as(rays_d)

  else:
    raise RuntimeError("please choose representation")

  if not flatten and N_rays < 0:
    rays_o = rearrange(rays_o, "b (h w) c -> b h w c", h=H, w=W)
    rays_d = rearrange(rays_d, "b (h w) c -> b h w c", h=H, w=W)
    select_inds = rearrange(select_inds, "b (h w) -> b h w", h=H, w=W)

  # [..., N_rays, 3]
  return rays_o, rays_d, select_inds


def parse_intrinsic(intr):
  """

  :param intr: (3, 3)
  :return:
  """

  fx = intr[0, 0]
  fy = intr[1, 1]
  cx = intr[0, 2]
  cy = intr[1, 2]
  return fx, fy, cx, cy


def get_rays_by_intr_and_extr(
        intrinsics,
        c2w,
        H: int,
        W: int,
        N_rays: int = -1,
        flatten=False,
        normalize_rays_d=False,
      **kwargs):
  """
  Support backprop.

  :param intrinsics: (3, 3)
  :param c2w: (b, 4, 4)
  :param H:
  :param W:
  :param N_rays:
  :param kwargs:
  :return:
  """

  device = c2w.device
  prefix = c2w.shape[:-2]  # [b, ]

  fx, fy, cx, cy = parse_intrinsic(intr=intrinsics)

  dirs, select_inds = _get_direction(H=H, W=W, focal_x=fx, focal_y=fy, center_x=cx, center_y=cy,
                                     prefix_dims=prefix, device=device, N_rays=N_rays,
                                     normalize_rays_d=normalize_rays_d)

  # (b, 3, 3)
  rot_m = c2w[..., :3, :3]
  # (b, 3)
  trans = c2w[..., :3, 3]

  # rotation: matrix multiplication, [..., N_rays, 1, 3] * [..., 1, 3, 3]
  rays_d = torch.sum(dirs[..., None, :] * rot_m[..., None, :, :], dim=-1)
  rays_o = trans[..., None, :].expand_as(rays_d)

  if not flatten and N_rays < 0:
    rays_o = rearrange(rays_o, "b (h w) c -> b h w c", h=H, w=W)
    rays_d = rearrange(rays_d, "b (h w) c -> b h w c", h=H, w=W)
    select_inds = rearrange(select_inds, "b (h w) -> b h w", h=H, w=W)

  return rays_o, rays_d, select_inds

def get_focal(f,
              H,
              W,
              intr_repr='square') -> Tuple[torch.Tensor, torch.Tensor]:
  """

  :param f:
  :param H:
  :param W:
  :param intr_repr:
  :return: (fx, fy)
  """
  if intr_repr == 'square':
    f = f ** 2
  elif intr_repr == 'ratio':
    f = f
  elif intr_repr == 'exp':
    f = torch.exp(f)
  else:
    raise RuntimeError("Please choose intr_repr")
  fx, fy = f
  fx = fx * W
  fy = fy * H
  return fx, fy


def get_rotation_matrix(rot,
                        representation='quaternion'):
  """

  :param rot: (b, 3)
  :param representation: ['axis-angle', ]
  :return: rot_m: (b, 3, 3)
  """
  if representation == 'axis-angle':
    assert rot.shape[-1] == 3
    # pytorch3d's implementation: axis-angle -> quaternion -> rotation matrix
    rot_m = tr3d.axis_angle_to_matrix(rot)
  elif representation == 'quaternion':
    assert rot.shape[-1] == 4
    quat = F.normalize(rot)
    rot_m = tr3d.quaternion_to_matrix(quat)  # [...,3,3]
  elif representation == 'rotation6D':
    assert rot.shape[-1] == 6
    rot_m = tr3d.rotation_6d_to_matrix(rot)
  else:
    raise RuntimeError("Please choose representation.")
  return rot_m


def get_camera2world(rot,
                     trans,
                     representation='quaternion'):
  """

  :param rot: (b, 3)
  :param trans: (b, 3)
  :param representation: ['axis-angle', ]
  :return: homo_m: (b, 4, 4)
  """
  assert rot.shape[:-1] == trans.shape[:-1]
  prefix = rot.shape[:-1]
  rot_m = get_rotation_matrix(rot, representation)
  tmp = torch.cat((rot_m.view(*prefix, 3, 3), trans.view(*prefix, 3, 1)), dim=-1)
  extend = torch.zeros(*prefix, 1, 4).to(rot.device)
  extend[..., 0, 3] = 1.
  homo_m = torch.cat((tmp, extend), dim=-2)  # [...,4,4]

  return homo_m  # [...,4,4]


class CamParams(nn.Module):
  def __init__(self,
               phi,
               t,
               f,
               H0=None,
               W0=None,
               so3_repr=None,
               intr_repr=None,
               freeze_intr=False,
               normalize_rays_d=False):
    super().__init__()
    # self.extra_attr_keys = []
    # self.register_extra_attr('so3_repr', so3_repr)
    # self.register_extra_attr('intr_repr', intr_repr)
    # self.register_extra_attr('H0', H0)  # used to calc focal length
    # self.register_extra_attr('W0', W0)  # used to calc focal length

    self.so3_repr = so3_repr
    self.intr_repr = intr_repr
    self.H0 = H0
    self.W0 = W0
    self.freeze_intr = freeze_intr
    self.normalize_rays_d = normalize_rays_d

    self.phi = nn.Parameter(phi)
    self.t = nn.Parameter(t) # initial value: 0
    self.f = nn.Parameter(f)
    pass

  @staticmethod
  def from_config(num_imgs=1,
                  H0: float = 1000,
                  W0: float = 1000,
                  so3_repr: str = 'axis-angle',
                  intr_repr: str = 'square',
                  initial_fov: float = 12,
                  freeze_intr=True,
                  normalize_rays_d=True):
    """
    # Camera parameters to optimize: phi, t, f
    # phi, t here is for camera2world

    :param num_imgs:
    :param H0:
    :param W0:
    :param so3_repr:
    :param intr_repr:
    :param initial_fov:
    :return:
    """


    if so3_repr == 'quaternion':
      phi = torch.tensor([1., 0., 0., 0.])

    elif so3_repr == 'axis-angle':
      phi = torch.tensor([0., 0., 0.])

    elif so3_repr == 'rotation6D':
      phi = torch.tensor([1., 0., 0., 0., 1., 0.])

    else:
      raise RuntimeError("Please choose representation")

    phi = phi[None, :].expand(num_imgs, -1)

    t = torch.zeros(num_imgs, 3)
    sx = 1. / np.tan((.5 * initial_fov * np.pi / 180.))
    sy = 1. / np.tan((.5 * initial_fov * np.pi / 180.))
    f = torch.tensor([sx, sy])

    if intr_repr == 'square':
      f = torch.sqrt(f)
    elif intr_repr == 'ratio':
      pass
    elif intr_repr == 'exp':
      f = torch.log(f)
    else:
      raise RuntimeError("Please choose intr_repr")

    m = CamParams(phi=phi.contiguous(),
                  t=t.contiguous(),
                  f=f.contiguous(),
                  H0=H0,
                  W0=W0,
                  so3_repr=so3_repr,
                  intr_repr=intr_repr,
                  freeze_intr=freeze_intr,
                  normalize_rays_d=normalize_rays_d)
    return m

  @staticmethod
  def from_state_dict(state_dict):
    m = CamParams(**state_dict)
    return m

  def forward(self,
              indices=None,
              mode='default'):
    """

    :param indices:
    :param mode: get_intrinsic,
    :return:

    """
    if mode == 'default':
      fx, fy = self.get_focal()
      return self.phi[indices], self.t[indices], fx, fy
    elif mode == 'get_intrinsic':
      if self.freeze_intr:
        self.f.requires_grad_(False)
      intr = self.get_intrinsic()
      return intr
    else:
      raise NotImplementedError

  def _get_random_pose(self,
                       bs,
                       r=1,
                       h_stddev=0.3,
                       v_stddev=0.155,
                       h_mean=np.pi * 0.5,
                       v_mean=np.pi * 0.5,
                       sample_dist='gaussian',
                       device='cuda'):
    """
    < opencv / colmap convention, standard pinhole camera >
    the camera is facing [+z] direction, x right, y downwards
          z
        ↗
      o------> x
      ↓
      y

    :param bs:
    :param r:
    :param h_stddev:
    :param v_stddev:
    :param h_mean:
    :param v_mean:
    :param sample_dist:
    :param device:
    :return

    - c2ws: (b, 4, 4)

    """

    camera_origin, pitch, yaw = geometry_tensor.sample_camera_positions(bs=bs,
                                                                        r=r,
                                                                        horizontal_stddev=h_stddev,
                                                                        vertical_stddev=v_stddev,
                                                                        horizontal_mean=h_mean,
                                                                        vertical_mean=v_mean,
                                                                        mode=sample_dist,
                                                                        device=device)

    # to opencv coordinate
    # camera_origin[:, 1] *= -1
    # camera_origin[:, 2] *= -1

    up = torch.zeros(bs, 3, device=device)
    up[:, 1] = 1
    focus_in_world = torch.zeros(bs, 3, device=device)

    # c2ws = geometry_tensor.look_at(cam_location=camera_origin, point=focus_in_world, up=up)
    # Cam points in positive -z direction
    forward_z = geometry_tensor.normalize(camera_origin - focus_in_world)
    c2ws = geometry_tensor.view_matrix(forward_z, up, camera_origin)

    return c2ws

  def get_rays_random_pose(self,
                           device,
                           bs,
                           # pixel coordinate to camera coordinate
                           intr=None,
                           H=None,
                           W=None,
                           # for random camera pose
                           r=1,
                           h_stddev=0.3,
                           v_stddev=0.155,
                           h_mean=np.pi * 0.5,
                           v_mean=np.pi * 0.5,
                           sample_dist='gaussian',
                           # for rays
                           N_rays: int = -1,
                           **kwargs):
    """
    :param intr: (3, 3)

    :return

    - rays_o: (b, H, W, 3)
    - rays_d: (b, H, W, 3)
    - select_inds: (b, H, W)
    """

    if intr is None:
      H, W = self.H0, self.W0
      intr = self.get_intrinsic(H, W, device=device)
    else:
      if H is None and W is None:
        H, W = self.H0, self.W0
      elif H is None or W is None:
        assert 0

    c2ws = self._get_random_pose(bs=bs,
                                 r=r,
                                 h_stddev=h_stddev,
                                 v_stddev=v_stddev,
                                 h_mean=h_mean,
                                 v_mean=v_mean,
                                 sample_dist=sample_dist,
                                 device=device)

    rays_o, rays_d, select_inds = get_rays_by_intr_and_extr(
      intrinsics=intr,
      c2w=c2ws,
      H=H,
      W=W,
      N_rays=N_rays,
      flatten=False,
      normalize_rays_d=self.normalize_rays_d)

    return rays_o, rays_d, select_inds

  def get_focal(self) -> Tuple[torch.Tensor, torch.Tensor]:
    """

    :return: (fx, fy)
    """
    return get_focal(f=self.f, H=self.H0, W=self.W0, intr_repr=self.intr_repr)

  @torch.no_grad()
  def get_rays_of_pose_avg(self,
                           H,
                           W,
                           bs=1):

    intr = self.get_intrinsic(H, W)
    c2ws = self.poses_avg()
    c2ws = c2ws.expand([bs, *c2ws.shape])

    rays_o, rays_d, select_inds = get_rays_by_intr_and_extr(intrinsics=intr,
                                                            c2w=c2ws,
                                                            H=H,
                                                            W=W,
                                                            N_rays=-1,
                                                            flatten=False)

    return rays_o, rays_d

  @torch.no_grad()
  def poses_avg(self):

    c2ws = self.get_camera2worlds()
    c2w_center = geometry_tensor.poses_avg(c2ws)
    return c2w_center

  def get_camera2worlds(self):
    """
    Support backprop.

    :return:
    """
    c2ws = get_camera2world(self.phi, self.t, self.so3_repr)
    return c2ws

  def get_intrinsic(self,
                    new_H=None,
                    new_W=None,
                    **kwargs):
    """
    Support backprop.

    :param new_H:
    :param new_W:
    :return: intr: (3, 3)
            [[fx, 0, cx]
             [0, fy, cy]
             [0, 0, 1]]
    """
    scale_x = new_W / self.W0 if new_W is not None else 1.
    scale_y = new_H / self.H0 if new_H is not None else 1.

    fx, fy = self.get_focal()

    intr = torch.eye(3, device=fx.device)
    cx = self.W0 / 2.
    cy = self.H0 / 2.
    # OK with grad: with produce grad_fn=<CopySlices>
    intr[0, 0] = fx * scale_x
    intr[1, 1] = fy * scale_y
    intr[0, 2] = cx * scale_x
    intr[1, 2] = cy * scale_y
    return intr

  def get_approx_bounds(self, near: float, far: float):
    fx, fy = get_focal(self.f.data.cpu(), self.H0, self.W0, self.intr_repr)
    rays_o, rays_d, _ = get_rays(self.phi.data.cpu(), self.t.data.cpu(), fx, fy, self.H0, self.W0, -1, self.so3_repr)
    rays_e = rays_o + rays_d * (far - near)
    rays_o = rays_o.reshape(-1, 3)
    rays_e = rays_e.reshape(-1, 3)
    all_points = np.concatenate([rays_o, rays_e], axis=0)
    min_points = np.min(all_points, axis=0)
    max_points = np.max(all_points, axis=0)
    return min_points, max_points

  # def register_extra_attr(self, k, v):
  #   self.__dict__[k] = v
  #   self.extra_attr_keys.append(k)

  # def load_state_dict(self,
  #                     state_dict,
  #                     strict: bool = True):
  #   # Load extra non-tensor parameters
  #   for k in self.extra_attr_keys:
  #     assert k in state_dict, 'could not found key: [{}] in state_dict'.format(k)
  #     self.__dict__[k] = state_dict[k]
  #   # Notice: DO NOT deep copy. we do not want meaningless memory usage
  #   nn_statedict = {}
  #   for k, v in state_dict.items():
  #     if k not in self.extra_attr_keys:
  #       nn_statedict[k] = v
  #   return super().load_state_dict(nn_statedict, strict=strict)
  #
  # def state_dict(self):
  #   sdict = super().state_dict()
  #   for k in self.extra_attr_keys:
  #     sdict[k] = self.__dict__[k]
  #   return sdict








# -----------------
# camera plotting utils
# -----------------

def about2index(about):
  if len(about) != 2:
    raise ValueError("Convention must have 2 letters.")
  if about[0] == about[1]:
    raise ValueError(f"Invalid convention {about}.")
  for letter in about:
    if letter not in ("x", "y", "z"):
      raise ValueError(f"Invalid letter {letter} in convention string.")
  letter2index = {'x': 0, 'y': 1, 'z': 2}
  i0 = letter2index[about[0]]
  i1 = letter2index[about[1]]
  return i0, i1


def plot_cam_trans(cam_param: CamParams, about='xy', return_img=False):
  # --------
  # get about index
  i0, i1 = about2index(about)

  fig = plt.figure()
  ax = fig.add_subplot(111)
  t = cam_param.t.data.cpu()
  # x, y, z = t.unbind(-1)
  t1, t2 = t[..., i0].numpy(), t[..., i1].numpy()
  ax.plot(t1, t2, '^-')

  if return_img:
    return utils.figure_to_image(fig)
  else:
    return fig


def plot_cam_rot(cam_param: CamParams, representation: str = 'quaternion', about='xy'):
  # --------
  # get about index
  i0, i1 = about2index(about)

  # ---------
  # plot
  fig = plt.figure()
  ax = fig.add_subplot(111)
  R = cam_param.phi.data.cpu()
  rot_m = get_rotation_matrix(R, representation)
  euler = tr3d.matrix_to_euler_angles(rot_m, 'XYZ')
  # rx, ry, rz = euler.unbind(-1)
  r1, r2 = euler[..., i0].numpy(), euler[..., i1].numpy()
  ax.plot(r1, r2, '^-')
  return fig
