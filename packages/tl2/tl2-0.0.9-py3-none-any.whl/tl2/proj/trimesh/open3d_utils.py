import os

import numpy as np
import open3d as o3d

from tl2 import tl2_utils
from tl2.proj.pil import pil_utils


def mesh_to_lineset(mesh,
                    color=[0.7, 0.7, 0.7]):
  mesh = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
  mesh.paint_uniform_color(color)
  return mesh

def create_mesh(verts,
                faces,
                mesh2lineset=True,
                color=[0.7, 0.7, 0.7]):
  """

  :param verts: (n, 3)
  :param faces: (m, 3)
  
  :return:
  """

  mesh = o3d.geometry.TriangleMesh()
  mesh.vertices = o3d.utility.Vector3dVector(verts)
  mesh.triangles = o3d.utility.Vector3iVector(faces)
  mesh.compute_vertex_normals()
  mesh.paint_uniform_color(color)

  if mesh2lineset:
    mesh = mesh_to_lineset(mesh=mesh, color=color)
    
  return mesh


def create_sphere_at_points(points,
                            radius=0.005,
                            color=[1.0, 0.0, 0.0]):
  geometries = o3d.geometry.TriangleMesh()
  for point in points:
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)  # create a small sphere to represent point
    sphere.translate(point)  # translate this sphere to point
    geometries += sphere
  geometries.paint_uniform_color(color)
  return geometries


def create_point_cloud(verts,
                       verts2sphere=False,
                       vert_size=0.01,
                       color=[1., 0., 0.]):
  if verts2sphere:
    pcl = create_sphere_at_points(verts, radius=vert_size, color=color)
  
  else:
    pcl = o3d.geometry.PointCloud()
    pcl.points = o3d.utility.Vector3dVector(verts)
    pcl.paint_uniform_color(color)
    # verts_pcl.colors = o3d.utility.Vector3dVector(colors)
  
  return pcl

  
def create_xyz_axis(size=0.3,
                    origin=np.array([0., 0., 0.])):
  axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=size, origin=origin)
  return axis


def show_geometries(geometries):
  # o3d.visualization.webrtc_server.enable_webrtc()
  
  viewer = o3d.visualization.Visualizer()
  viewer.create_window()
  
  for geometry in geometries:
    viewer.add_geometry(geometry)
  
  opt = viewer.get_render_option()
  # opt.show_coordinate_frame = True
  
  # opt.mesh_show_wireframe = True
  # opt.background_color = np.asarray([0.5, 0.5, 0.5])
  
  viewer.run()
  viewer.destroy_window()
  pass


def _add_3d_label(verts, verts_pcl):
  app = o3d.visualization.gui.Application.instance
  app.initialize()

  vis = o3d.visualization.O3DVisualizer()
  vis.show_settings = True

  # for geometry in geometries:
  #   vis.add_geometry(geometry)
  vis.add_geometry('Points', verts_pcl)
  for idx in range(0, len(verts)):
    vis.add_3d_label(verts[idx], f"{idx}")

  vis.reset_camera_to_default()
  app.add_window(vis)
  app.run()
  pass


def show_smpl(verts,
              faces,
              mesh2lineset=True,
              face_color=[0.7, 0.7, 0.7],
              joints=None,
              joints2sphere=False,
              joints_size=0.01,
              axis_size=0.2,
              show=False,
              ):
  """
  https://github.com/vchoutas/smplx/blob/master/examples/demo.py
  
  :param mesh:
  :param show:
  :param verts:
  :return:
  """
  
  geometries = []
  
  # mesh
  body_mesh = create_mesh(verts=verts, faces=faces, mesh2lineset=mesh2lineset, color=face_color)
  geometries.append(body_mesh)
  
  # joints
  if joints is not None:
    pcl = create_point_cloud(verts=joints, verts2sphere=joints2sphere, vert_size=joints_size)
    geometries.append(pcl)
  
  # xyz axis
  if axis_size > 0:
    axis = create_xyz_axis(size=axis_size)
    geometries.append(axis)
  
  if show:
    o3d.visualization.draw_geometries(geometries)
  
  return geometries


def draw_geometries(geometries):
  o3d.visualization.draw_geometries(geometries)
  pass


def tensorboard_import():
  import open3d as o3d
  # Monkey-patch torch.utils.tensorboard.SummaryWriter
  # Utility function to convert Open3D geometry to a dictionary format
  from open3d.visualization.tensorboard_plugin import summary
  from open3d.visualization.tensorboard_plugin.util import to_dict_batch
  from torch.utils.tensorboard import SummaryWriter
  
  return o3d, to_dict_batch, SummaryWriter


def add_geometries(vis,
                   geometries):
  if not isinstance(geometries, (list, tuple)):
    geometries = [geometries]
    
  for geo in geometries:
    vis.add_geometry(geo)
  pass


def remove_geometries(vis,
                      geometries):
  if not isinstance(geometries, (list, tuple)):
    geometries = [geometries]
  
  for geo in geometries:
    vis.remove_geometry(geo)
  pass


class NonBlock_Visualization(object):
  
  def __init__(self,
               width=1920,
               height=1080,
               cam_json=None):
    
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=width, height=height)
    
    self.vis = vis

    self.img_size = None
    
    if cam_json is not None:
      self.cam_params = self.read_pinhole_camera(cam_json=cam_json)
    else:
      self.cam_params = None
    
    pass
  
  def add_geometries(self,
                     geometries):
    add_geometries(self.vis, geometries)
    pass
  
  def render_frame(self,
                   frame_id=None,
                   outdir=None,
                   fixed_cam=False):
    """
    
    :param frame_id: whether save to image
    :param outdir:
    :param fixed_cam:
    :return:
    """
    if fixed_cam and self.cam_params is not None:
      self.set_view_control(cam_params=self.cam_params)
    
    # vis.update_geometry(source)
    self.vis.poll_events()
    self.vis.update_renderer()

    img_pil = None
    if frame_id is not None:
      img_pil = self.frame_to_pil(frame_id=frame_id,
                                  outdir=outdir)

    return img_pil
  
  def remove_geometries(self,
                        geometries):
    remove_geometries(vis=self.vis, geometries=geometries)
    pass
    
  def release(self,
              block=True):
    if block:
      self.vis.run()
    self.vis.destroy_window()
    pass
    
  def frame_to_pil(self,
                   frame_id,
                   outdir):
    if outdir is None:
      outdir = tl2_utils.get_tempdir().name
    os.makedirs(outdir, exist_ok=True)
    img_path = f"{outdir}/{frame_id:0>6}.jpg"
    self.vis.capture_screen_image(img_path, do_render=True)
    
    img_pil = pil_utils.pil_open_rgb(img_path)
    if self.img_size is None:
      self.img_size = img_pil.size
    img_pil = pil_utils.pil_resize(img_pil, self.img_size)
    
    return img_pil
  
  def read_pinhole_camera(self,
                          cam_json):
    parameters = o3d.io.read_pinhole_camera_parameters(cam_json)
    return parameters
  
  def set_view_control(self,
                       cam_params):
    ctr = self.vis.get_view_control()
    ctr.convert_from_pinhole_camera_parameters(cam_params)
    pass
  