import sys
# sys.path.insert(0, 'tl2_lib')
import shutil
import os
import sys
import numpy as np
import imageio
import streamlit as st

sys.path.insert(0, os.getcwd())

import open3d as o3d
from open3d.visualization.tensorboard_plugin import summary
from open3d.visualization.tensorboard_plugin.util import to_dict_batch
from torch.utils.tensorboard import SummaryWriter

from tl2.launch.launch_utils import update_parser_defaults_from_yaml, global_cfg
from tl2 import tl2_utils
from tl2.proj.fvcore import MODEL_REGISTRY
from tl2.proj.cv2 import cv2_utils
from tl2.proj.pil import pil_utils
from tl2.proj.streamlit import st_utils

# sys.path.insert(0, f"{os.getcwd()}/DGP_lib")
# from DGP_lib import utils
# sys.path.pop(0)


def build_sidebar():
  st.sidebar.text(global_cfg.sidebar.sidebar_name)
  st.sidebar.text(f"{global_cfg.tl_outdir}")
  pass


@MODEL_REGISTRY.register(name_prefix=__name__)
class STModel(object):
  def __init__(self):
    
    pass
  
  def simple_geometry(self,
                      cfg,
                      outdir,
                      saved_suffix_state=None,
                      **kwargs):
    
    fps = st_utils.number_input('fps', cfg.fps, sidebar=True)
    
    if not global_cfg.tl_debug:
      if not st.sidebar.button("run_web"):
        return
    
    if saved_suffix_state is not None:
      saved_suffix_state.saved_suffix = saved_suffix_state.saved_suffix + 1
    
    device = 'cuda'
    
    # o3d, to_dict_batch, SummaryWriter = open3d_utils.tensorboard_import()

    import importlib
    import open3d as o3d
    from open3d.visualization.tensorboard_plugin import summary
    from open3d.visualization.tensorboard_plugin.util import to_dict_batch
    from torch.utils.tensorboard import SummaryWriter

    if hasattr(SummaryWriter, "add_3d"):
      del SummaryWriter.add_3d
    importlib.reload(o3d)
    importlib.reload(summary)
    

    cube = o3d.geometry.TriangleMesh.create_box(1, 2, 4)
    cube.compute_vertex_normals()
    cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=1.0,
                                                         height=2.0,
                                                         resolution=20,
                                                         split=4)
    cylinder.compute_vertex_normals()
    colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]

    logdir = f"results/open3d_tensorboard/open3d_tensorbard_web/o3d"
    shutil.rmtree(logdir, ignore_errors=True)
    os.makedirs(logdir, exist_ok=True)
    writer = SummaryWriter(logdir)
    for step in range(3):
      cube.paint_uniform_color(colors[step])
      # open3d_utils.show_geometries([cube])
      writer.add_3d('cube', to_dict_batch([cube]), step=step)
  
      cylinder.paint_uniform_color(colors[step])
      writer.add_3d('cylinder', to_dict_batch([cylinder]), step=step)

    writer.close()
    tensorboard_command = f"tensorboard --logdir {os.path.dirname(logdir)}"
    print(tensorboard_command)

    pass



if __name__ == '__main__':
  """
  export PYTHONPATH=.:./tl2_lib
  python -u tl2_lib/tl2/proj/trimesh/examples/open3d/open3d_tensorboard.py
  
  """
  # import open3d as o3d
  # # Monkey-patch torch.utils.tensorboard.SummaryWriter
  # # Utility function to convert Open3D geometry to a dictionary format
  # from open3d.visualization.tensorboard_plugin import summary
  # from open3d.visualization.tensorboard_plugin.util import to_dict_batch
  # from torch.utils.tensorboard import SummaryWriter

  import importlib
  importlib.reload(o3d)
  
  
  cube = o3d.geometry.TriangleMesh.create_box(1, 2, 4)
  cube.compute_vertex_normals()
  cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=1.0,
                                                       height=2.0,
                                                       resolution=20,
                                                       split=4)
  cylinder.compute_vertex_normals()
  colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]

  logdir = f"results/open3d_tensorboard/open3d_tensorbard_web/o3d"
  shutil.rmtree(logdir, ignore_errors=True)
  os.makedirs(logdir, exist_ok=True)
  writer = SummaryWriter(logdir)
  for step in range(3):
    cube.paint_uniform_color(colors[step])
    # open3d_utils.show_geometries([cube])
    writer.add_3d('cube', to_dict_batch([cube]), step=step)

    cylinder.paint_uniform_color(colors[step])
    writer.add_3d('cylinder', to_dict_batch([cylinder]), step=step)

  writer.close()
  tensorboard_command = f"tensorboard --logdir {os.path.dirname(logdir)}"
  print(tensorboard_command)