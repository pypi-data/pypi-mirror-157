import numpy as np
import math
import random

import torch
import torch.nn.functional as F


def _truncated_normal(tensor, mean=0, std=1):
  size = tensor.shape
  tmp = tensor.new_empty(size + (4,)).normal_()
  valid = (tmp < 2) & (tmp > -2)
  ind = valid.max(-1, keepdim=True)[1]
  tensor.data.copy_(tmp.gather(-1, ind).squeeze(-1))
  tensor.data.mul_(std).add_(mean)
  return tensor


def sample_camera_positions(device,
                            bs=1,
                            r=1,
                            horizontal_stddev=1,
                            vertical_stddev=1,
                            horizontal_mean=math.pi * 0.5,
                            vertical_mean=math.pi * 0.5,
                            mode='normal'):
  """
  Samples bs random locations along a sphere of radius r. Uses the specified distribution.
       y
      |
      --> x
    /
   z
  :param device:
  :param bs:
  :param r:
  :param horizontal_stddev: yaw std
  :param vertical_stddev: pitch std
  :param horizontal_mean:
  :param vertical_mean:
  :param mode:
  :return

  - output_points: (bs, 3), camera positions
  - phi: (bs, 1), pitch in radians [0, pi]
  - theta: (bs, 1), yaw in radians [-pi, pi]
  """

  if mode == 'uniform':
    theta = (torch.rand((bs, 1), device=device) - 0.5) \
            * 2 * horizontal_stddev \
            + horizontal_mean
    phi = (torch.rand((bs, 1), device=device) - 0.5) \
          * 2 * vertical_stddev \
          + vertical_mean

  elif mode == 'normal' or mode == 'gaussian':
    theta = torch.randn((bs, 1), device=device) \
            * horizontal_stddev \
            + horizontal_mean
    phi = torch.randn((bs, 1), device=device) \
          * vertical_stddev \
          + vertical_mean

  elif mode == 'hybrid':
    if random.random() < 0.5:
      theta = (torch.rand((bs, 1), device=device) - 0.5) \
              * 2 * horizontal_stddev * 2 \
              + horizontal_mean
      phi = (torch.rand((bs, 1), device=device) - 0.5) \
            * 2 * vertical_stddev * 2 \
            + vertical_mean
    else:
      theta = torch.randn((bs, 1), device=device) * horizontal_stddev + horizontal_mean
      phi = torch.randn((bs, 1), device=device) * vertical_stddev + vertical_mean

  elif mode == 'truncated_gaussian':
    theta = _truncated_normal(torch.zeros((bs, 1), device=device)) \
            * horizontal_stddev \
            + horizontal_mean
    phi = _truncated_normal(torch.zeros((bs, 1), device=device)) \
          * vertical_stddev \
          + vertical_mean

  elif mode == 'spherical_uniform':
    theta = (torch.rand((bs, 1), device=device) - .5) \
            * 2 * horizontal_stddev \
            + horizontal_mean
    v_stddev, v_mean = vertical_stddev / math.pi, vertical_mean / math.pi
    v = ((torch.rand((bs, 1), device=device) - .5) * 2 * v_stddev + v_mean)
    v = torch.clamp(v, 1e-5, 1 - 1e-5)
    phi = torch.arccos(1 - 2 * v)

  elif mode == 'mean':
    # Just use the mean.
    theta = torch.ones((bs, 1), device=device, dtype=torch.float) * horizontal_mean
    phi = torch.ones((bs, 1), device=device, dtype=torch.float) * vertical_mean
  else:
    assert 0

  phi = torch.clamp(phi, 1e-5, math.pi - 1e-5)

  output_points = torch.zeros((bs, 3), device=device) # (bs, 3)
  output_points[:, 0:1] = r * torch.sin(phi) * torch.cos(theta) # x
  output_points[:, 2:3] = r * torch.sin(phi) * torch.sin(theta) # z
  output_points[:, 1:2] = r * torch.cos(phi) # y

  return output_points, phi, theta


def normalize(vec):
    # return vec / (vec.norm(dim=-1, keepdim=True) + 1e-9)
    return F.normalize(vec, p=2, dim=-1)


def poses_avg(poses):
    center = poses[:, :3, 3].mean(0)
    forward = poses[:, :3, 2].sum(0)
    up = poses[:, :3, 1].sum(0)
    c2w = view_matrix(forward, up, center)
    return c2w


""" All following opencv convenrtion
    < opencv / colmap convention, standard pinhole camera >
    the camera is facing [+z] direction, x right, y downwards
                z
               ↗
            o------> x
            ↓ 
            y
"""


def look_at(
    cam_location,
    point,
    up):
    # Cam points in positive z direction
    forward = normalize(point - cam_location)     # openCV convention

    return view_matrix(forward, up, cam_location)


def view_matrix(
      forward,
      up,
      cam_location):

    rot_z = normalize(forward)
    rot_x = normalize(torch.cross(up, rot_z))
    rot_y = normalize(torch.cross(rot_z, rot_x))
    mat = torch.stack((rot_x, rot_y, rot_z, cam_location), dim=-1)

    hom_vec = torch.tensor([[0., 0., 0., 1.]], device=forward.device)
    if len(mat.shape) > 2:
        hom_vec = hom_vec.expand([mat.shape[0], -1, -1])
    mat = torch.cat((mat, hom_vec), dim=-2)
    return mat


def c2w_track_spiral(c2w,
                     up_vec,
                     rads,
                     focus: float,
                     zrate: float,
                     rots: int,
                     N: int,
                     **kwargs):
    # TODO: support zdelta
    """generate camera to world matrices of spiral track, looking at the same point [0,0,focus]

    Args:
        c2w ([4,4] or [3,4]):   camera to world matrix (of the spiral center,
                                  with average rotation and average translation)
        up_vec ([3,]):          vector pointing up
        rads ([3,]):            radius of x,y,z direction, of the spiral track
        # zdelta ([float]):       total delta z that is allowed to change 
        focus (float):          a focus value (to be looked at) (in camera coordinates)
        zrate ([float]):        a factor multiplied to z's angle
        rots ([int]):           number of rounds to rotate
        N ([int]):              number of total views
    """

    c2w_tracks = []
    rads = np.array(list(rads) + [1.])
    
    # focus_in_cam = np.array([0, 0, -focus, 1.])   # openGL convention
    focus_in_cam = np.array([0, 0, focus, 1.])      # openCV convention
    focus_in_world = np.dot(c2w[:3, :4], focus_in_cam)

    for theta in np.linspace(0., 2. * np.pi * rots, N+1)[:-1]:
        cam_location = np.dot(
            c2w[:3, :4], 
            # np.array([np.cos(theta), -np.sin(theta), -np.sin(theta*zrate), 1.]) * rads    # openGL convention
            np.array([np.cos(theta), np.sin(theta), np.sin(theta*zrate), 1.]) * rads        # openCV convention
        )
        c2w_i = look_at(cam_location, focus_in_world, up=up_vec)
        c2w_tracks.append(c2w_i)

    return c2w_tracks