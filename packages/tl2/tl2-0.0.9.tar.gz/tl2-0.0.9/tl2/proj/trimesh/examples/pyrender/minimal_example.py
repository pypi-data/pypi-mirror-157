import trimesh
import pyrender

"""
python tl2_lib/tl2/proj/trimesh/examples/pyrender/minimal_example.py

"""

fuze_trimesh = trimesh.load('models/fuze.obj')
mesh = pyrender.Mesh.from_trimesh(fuze_trimesh)
scene = pyrender.Scene()
scene.add(mesh)
pyrender.Viewer(scene, use_raymond_lighting=True)
