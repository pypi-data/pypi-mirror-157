import trimesh


def create_mesh(verts,
                faces,
                process=False):
  """
  
  :param verts: (n, 3)
  :param faces: (m, 3)
  :param process:
  :return:
  """
  
  mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=process)
  return mesh


def show_mesh(mesh,
              show=False,
              verts=None):
  """
  
  :param mesh:
  :param show:
  :param verts: (n, 3)
  :return:
  """
  
  scene = trimesh.scene.scene.Scene()
  
  scene.add_geometry(mesh)

  if verts is not None:
    from tl2.proj.matplot import plt_utils
    
    N_pts = len(verts)
    colors = plt_utils.get_colors_by_cmap(N_colors=N_pts, )

    # metadata = {idx: f"{idx}" for idx in range(N_pts)}
    cloud_pts = trimesh.PointCloud(vertices=verts, colors=colors)
    scene.add_geometry(cloud_pts)
  
  if show:
    scene.show()
    
  return scene