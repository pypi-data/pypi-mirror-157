"""
- Install:
  pip install pyrender PyOpenGL-accelerate
  sudo apt install -y freeglut3-dev

- ImportError: cannot import name 'EGLPlatform' from 'pyrender.platforms'
  pip install --no-cache-dir -I pyrender
  pyrender==0.1.45

- ImportError: cannot import name 'OSMesaCreateContextAttribs' from 'OpenGL.osmesa'
  pip install pyopengl==3.1.6

export EGL_DEVICE_ID=1

"""
import os
import sys
from inspect import currentframe, getframeinfo
import numpy as np
import trimesh

def get_pyopengl_platform():

  code_str = f'''\
    {sys.executable} -c\
    "import os;\
    os.environ['PYOPENGL_PLATFORM'] = 'egl';\
    os.environ['MESA_GL_VERSION_OVERRIDE'] = '4.1';\
    import pyrender;\
    _ = pyrender.OffscreenRenderer(\
      viewport_width=128,\
      viewport_height=128,\
      point_size=1.0\
      )"\
    '''.strip()
  
  ret = os.system(code_str)

  # fix bugs: munmap_chunk(): invalid pointer
  import torch
  
  if ret == 0:
    # fix bugs: err = 12297
    os.environ['MESA_GL_VERSION_OVERRIDE'] = '4.1'
    print(f"{'*' * 6} pyrender platform: egl {'*' * 6}")
    return 'egl'
  else:
    frameinfo = getframeinfo(currentframe())
    print(f"{__name__}, line{frameinfo.lineno}:")
    print(f"{'*' * 6} Failed to using egl {'*' * 6}")
    print(f"{'*' * 6} pyrender platform: osmesa {'*' * 6}")
    return 'osmesa'
  
PYOPENGL_PLATFORM = get_pyopengl_platform()
os.environ['PYOPENGL_PLATFORM'] = PYOPENGL_PLATFORM
import pyrender
_ = pyrender.OffscreenRenderer(
      viewport_width=128,
      viewport_height=128,
      point_size=1.0
    )


def show_smpl(verts,
              faces,
              joints=None,
              show=False
              ):
  
  geometries = []
  # mesh
  vertex_colors = np.ones([verts.shape[0], 4]) * [0.3, 0.3, 0.3, 0.8]
  tri_mesh = trimesh.Trimesh(verts,
                             faces,
                             vertex_colors=vertex_colors)
  
  mesh = pyrender.Mesh.from_trimesh(tri_mesh)
  geometries.append(mesh)
  
  # joints
  if joints is not None:
    sm = trimesh.creation.uv_sphere(radius=0.005)
    sm.visual.vertex_colors = [0.9, 0.1, 0.1, 1.0]
    tfs = np.tile(np.eye(4), (len(joints), 1, 1))
    tfs[:, :3, 3] = joints
    joints_pcl = pyrender.Mesh.from_trimesh(sm, poses=tfs)
    
    geometries.append(joints_pcl)
  
  if show:
    scene = pyrender.Scene()
    for geo in geometries:
      scene.add(geo)
    pyrender.Viewer(scene, use_raymond_lighting=True)
  
  
def create_scene():
  """
  scene.add(mesh)
  pyrender.Viewer(scene, use_raymond_lighting=True)
  
  :return:
  """
  scene = pyrender.Scene()
  return scene


def viewer(scene):
  pyrender.Viewer(scene, use_raymond_lighting=True)
  pass




