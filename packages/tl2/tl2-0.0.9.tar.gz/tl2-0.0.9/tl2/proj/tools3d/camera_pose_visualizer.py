from matplotlib.ticker import MaxNLocator
import sys
import os
import unittest
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from tl2.proj.matplot import plt_utils


class CameraPoseVisualizer:
  def __init__(self,
               xlim=[-1, 1],
               ylim=[-1, 1],
               zlim=[-0.2, 1.2],
               xyz_mode='xyz2zxy',
               figsize=(10.24, 10.24),
               labelsize=30,
               ticksize=20,
               labelpad=15,
               elev=20,
               azim=30,
               show_label=False,
               N_frames=None):
    self.cmap = mpl.cm.rainbow
    self.xyz_mode = xyz_mode
    self.N_frames = N_frames

    if xyz_mode == 'xyz':
      xlabel = 'x'
      ylabel= 'y'
      zlabel = 'z'
    elif xyz_mode == 'xyz2zxy':
      xlim, ylim, zlim = zlim, xlim, ylim
      xlabel, ylabel, zlabel = 'z', 'x', 'y'
    else:
      raise NotImplemented

    plt.style.use('seaborn-paper')
    plt_utils.set_times_new_roman_font()

    self.fig = plt.figure(figsize=figsize)
    self.ax = self.fig.add_subplot(1, 1, 1, projection='3d')
    padding = 0.0
    self.fig.subplots_adjust(left=padding, bottom=padding, right=1 - padding, top=1 - padding)

    def setup_ax():

      self.ax.set_aspect("auto")
      self.ax.set_xlim(xlim)
      self.ax.set_ylim(ylim)
      self.ax.set_zlim(zlim)

      # fontsize = 30
      if show_label:
        self.ax.set_xlabel(xlabel, fontsize=labelsize, labelpad=labelpad)
        self.ax.set_ylabel(ylabel, fontsize=labelsize, labelpad=labelpad)
        self.ax.set_zlabel(zlabel, fontsize=labelsize, labelpad=labelpad)

      self.ax.yaxis.set_major_locator(MaxNLocator(5))
      self.ax.xaxis.set_major_locator(MaxNLocator(5))
      self.ax.zaxis.set_major_locator(MaxNLocator(5))
      self.ax.tick_params(labelsize=ticksize)

      self.ax.grid(visible=True, which='major', color='#666666', linestyle='--', alpha=0.2)

      self.ax.view_init(elev=elev, azim=azim)

    setup_ax()

    self.setup_ax = setup_ax
    pass

  def _get_xyz(self, xyz):
    if self.xyz_mode == 'xyz':
      return xyz
    elif self.xyz_mode == 'xyz2zxy':
      return xyz[2], xyz[0], xyz[1]
    else:
      raise NotImplemented

  def extrinsic2pyramid(self,
                        extrinsic,
                        color='r',
                        focal_len_scaled=0.1,
                        height=0.3,
                        aspect_ratio=1,
                        cur_frame=None):
    """

    :param extrinsic: (4, 4)
    :param color: r, c, k
    :param focal_len_scaled:
    :param aspect_ratio:
    :return:
    """
    self.ax.clear()
    self.setup_ax()

    if extrinsic.shape == (3, 4):
      extrinsic = np.vstack([extrinsic, [0, 0, 0, 1]])
      pass

    vertex_std = np.array([[0, 0, 0, 1],
                           [focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, -height, 1],
                           [focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, -height, 1],
                           [-focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, -height, 1],
                           [-focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, -height, 1]])
    vertex_transformed = vertex_std @ extrinsic.T


    # meshes = [[vertex_transformed[0, :-1], vertex_transformed[1][:-1], vertex_transformed[2, :-1]],
    #           [vertex_transformed[0, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1]],
    #           [vertex_transformed[0, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]],
    #           [vertex_transformed[0, :-1], vertex_transformed[4, :-1], vertex_transformed[1, :-1]],
    #           [vertex_transformed[1, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1],
    #            vertex_transformed[4, :-1]]]
    meshes = [
      # [vertex_transformed[0, :-1], vertex_transformed[1][:-1], vertex_transformed[2, :-1]],
      [self._get_xyz(vertex_transformed[0, :-1]), self._get_xyz(vertex_transformed[1][:-1]), self._get_xyz(vertex_transformed[2, :-1])],
      # [vertex_transformed[0, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1]],
      [self._get_xyz(vertex_transformed[0, :-1]), self._get_xyz(vertex_transformed[2, :-1]), self._get_xyz(vertex_transformed[3, :-1])],
      # [vertex_transformed[0, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]],
      [self._get_xyz(vertex_transformed[0, :-1]), self._get_xyz(vertex_transformed[3, :-1]), self._get_xyz(vertex_transformed[4, :-1])],
      # [vertex_transformed[0, :-1], vertex_transformed[4, :-1], vertex_transformed[1, :-1]],
      [self._get_xyz(vertex_transformed[0, :-1]), self._get_xyz(vertex_transformed[4, :-1]), self._get_xyz(vertex_transformed[1, :-1])],
      # [vertex_transformed[1, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]]
      [self._get_xyz(vertex_transformed[1, :-1]), self._get_xyz(vertex_transformed[2, :-1]), self._get_xyz(vertex_transformed[3, :-1]), self._get_xyz(vertex_transformed[4, :-1])],
    ]

    if cur_frame is not None:
      color = self.cmap((cur_frame + 1) / self.N_frames)
    self.ax.add_collection3d(
      Poly3DCollection(meshes, facecolors=color, linewidths=1., edgecolors='black', alpha=0.35))

    # circle h
    phi = np.linspace(0, np.pi, 100)
    x = np.cos(phi)
    z = np.sin(phi)
    y = np.zeros_like(x)
    x, y, z = self._get_xyz([x, y, z])

    color_circle = plt_utils.colors_dict['grey']
    self.ax.plot(x, y, z, color_circle)
    self.ax.plot([x[0], x[-1]], [y[0], y[-1]], [z[0], z[-1]], color_circle)

    # circle v
    phi = np.linspace(0, np.pi, 100)
    y = np.cos(phi)
    z = np.sin(phi)
    x = np.zeros_like(y)
    x, y, z = self._get_xyz([x, y, z])

    self.ax.plot(x, y, z, color_circle)
    self.ax.plot([x[0], x[-1]], [y[0], y[-1]], [z[0], z[-1]], color_circle)

    # plot xyz axis
    axis_length = 0.3
    fontsize = 20
    linewidth = 3
    # x
    x, y, z = self._get_xyz([[0, axis_length], [0, 0], [0, 0]])
    self.ax.plot(x, y, z, 'red', linewidth=linewidth)
    x, y, z = self._get_xyz([axis_length, 0, 0])
    self.ax.text(x, y, z, s=f'x', color='red',
                 # zdir='x',
                 ha='left',
                 va='bottom',
                 fontsize=fontsize,
                 )
    # y
    x, y, z = self._get_xyz([[0, 0], [0, axis_length], [0, 0]])
    self.ax.plot(x, y, z, 'green', linewidth=linewidth)
    x, y, z = self._get_xyz([0, axis_length, 0])
    self.ax.text(x, y, z, s=f'y', color='green',
                 # zdir='x',
                 ha='right',
                 va='baseline',
                 fontsize=fontsize
                 )
    # z
    x, y, z = self._get_xyz([[0, 0], [0, 0], [0, axis_length]])
    self.ax.plot(x, y, z, 'blue', linewidth=linewidth)
    x, y, z = self._get_xyz([0, 0, axis_length])
    self.ax.text(x, y, z, s=f'z', color='blue',
                 # zdir='x',
                 ha='right',
                 va='top',
                 fontsize=fontsize
                 )

    pass

  def customize_legend(self,
                       list_label):
    list_handle = []
    for idx, label in enumerate(list_label):
      color = plt.cm.rainbow(idx / len(list_label))
      patch = Patch(color=color, label=label)
      list_handle.append(patch)
    plt.legend(loc='right', bbox_to_anchor=(1.8, 0.5), handles=list_handle)

  def colorbar(self,
               max_frame_length,
               label='Frame Number',
               orientation='horizontal'):
    """

    :param max_frame_length:
    :param label:
    :param orientation: vertical, horizontal
    :return:
    """
    cmap = self.cmap
    norm = mpl.colors.Normalize(vmin=0, vmax=max_frame_length)

    from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size

    # divider = make_axes_locatable(self.ax)
    # width = axes_size.AxesY(self.ax, aspect=1. / 20)
    # pad = axes_size.Fraction(0.5, width)
    # cax = divider.append_axes("right", size=width, pad=pad)

    cbar = self.fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                             orientation=orientation,
                             label=label,
                             # cax=cax
                             # fraction=0.03,
                             pad=0, # space between axes
                             )

    pass

  def show(self):
    plt.title('Extrinsic Parameters')
    plt.show()

  def to_pil(self):
    fig_pil = plt_utils.fig_to_pil(self.fig)
    return fig_pil


class Testing_CameraPoseVisualizer(unittest.TestCase):

  def test_extrinsic2pyramid(self, debug=True):
    """
    Usage:

        # export CUDA_VISIBLE_DEVICES=$cuda_devices
        # export RUN_NUM=$run_num

        export CUDA_VISIBLE_DEVICES=0
        export PORT=12345
        export TIME_STR=1
        export PYTHONPATH=.:tl2_lib
        python -c "from exp.camera_pose_visualizer import Testing_CameraPoseVisualizer;\
          Testing_CameraPoseVisualizer().test_extrinsic2pyramid(debug=False)"

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    if 'RUN_NUM' not in os.environ:
      os.environ['RUN_NUM'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')

    if debug:
      # sys.argv.extend(['--tl_outdir', 'results/train_ffhq_256/train_ffhq_256-test'])
      pass
    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    resume = os.path.isdir(f"{outdir}/ckptdir/resume") and \
             tl2_utils.parser_args_from_list(name="--tl_outdir", argv_list=sys.argv, type='str') is not None
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pil import pil_utils

    visualizer = CameraPoseVisualizer(N_frames=2)

    extri = np.eye(4)
    extri[2, 3] = 1
    visualizer.extrinsic2pyramid(extri, cur_frame=0)

    extri = np.eye(4)
    extri[2, 3] = 0.4
    extri[0, 3] = 0.3
    visualizer.extrinsic2pyramid(extri, cur_frame=1)

    # visualizer.colorbar(max_frame_length)
    img_pil = visualizer.to_pil()
    # pil_utils.imshow_pil(img_pil, f"{img_pil.size}")
    visualizer.show()

    os.makedirs('cached_pretrained', exist_ok=True)
    img_pil.save(f"cached_pretrained/demo1.jpg")

    pass