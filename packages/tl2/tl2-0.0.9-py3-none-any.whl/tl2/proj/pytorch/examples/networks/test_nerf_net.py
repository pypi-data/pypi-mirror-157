import os
import sys
import unittest
import argparse
from einops import rearrange

import torch


class Testing_nerf_net(unittest.TestCase):

  def test__build_PosEmbedding(self, debug=True):
    """
    Usage:

        # export CUDA_VISIBLE_DEVICES=$cuda_devices
        # export RUN_NUM=$run_num

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export PORT=12345
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts root_obs s3://$bucket/ZhouPeng/ \
          --tl_outdir results/train_ffhq_256/train_ffhq_256-20210726_202423_412
          # --tl_outdir results/$resume_dir

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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/nerf_net.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import nerf_net

    net = nerf_net.PosEmbedding(**cfg).cuda()

    bs = 4
    N = 10
    in_dim = 3

    x = torch.rand(bs, N, in_dim, requires_grad=True).cuda()

    out = net(x)

    pass

  def test__build_NeRFNetwork_CIPS(self, debug=True):
    """
    Usage:

        # export CUDA_VISIBLE_DEVICES=$cuda_devices
        # export RUN_NUM=$run_num

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export PORT=12345
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts root_obs s3://$bucket/ZhouPeng/ \
          --tl_outdir results/train_ffhq_256/train_ffhq_256-20210726_202423_412
          # --tl_outdir results/$resume_dir

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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/nerf_net.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import nerf_net
    from . import multi_head_mapping
    from ..nerf import volume_rendering
    from ..nerf import cam_params

    net = nerf_net.NeRFNetwork_CIPS(**cfg).cuda()

    bs = 4
    H = 64
    W = 64

    cam_param = cam_params.CamParams.from_config(num_imgs=1,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr='axis-angle',
                                                 intr_repr='square',
                                                 initial_fov=53.13,
                                                 freeze_intr=False).cuda()

    intr = cam_param(mode='get_intrinsic')

    rays_o, rays_d, select_inds = cam_param.get_rays_random_pose(
      device='cuda',
      bs=bs,
      intr=intr,
      h_stddev=0.3,
      v_stddev=0.155,
    )

    rays_o = rearrange(rays_o, "b h w c -> b (h w) c", h=H, w=W)
    rays_d = rearrange(rays_d, "b h w c -> b (h w) c", h=H, w=W)

    z_vals, points = volume_rendering.ray_sample_points(rays_o=rays_o,
                                                        rays_d=rays_d,
                                                        near=0.5,
                                                        far=1.5,
                                                        N_samples=24,
                                                        perturb=0)

    print(f"x range: [{points[..., 0].min()}, {points[..., 0].max()}]")
    print(f"y range: [{points[..., 1].min()}, {points[..., 1].max()}]")
    print(f"z range: [{points[..., 2].min()}, {points[..., 2].max()}]")

    z_dim = 128
    style_dim = 128

    mapping_shape = multi_head_mapping.MultiHeadMappingNetwork(z_dim=z_dim,
                                                               hidden_dim=z_dim,
                                                               base_layers=4,
                                                               head_layers=0,
                                                               head_dim_dict=net.style_dim_dict_shape,
                                                               add_norm=True,
                                                               norm_out=True).cuda()
    mapping_app = multi_head_mapping.MultiHeadMappingNetwork(z_dim=z_dim,
                                                             hidden_dim=z_dim,
                                                             base_layers=4,
                                                             head_layers=0,
                                                             head_dim_dict=net.style_dim_dict_app,
                                                             add_norm=True,
                                                             norm_out=True).cuda()

    z_shape = torch.randn(bs, z_dim).cuda()
    z_app = torch.randn(bs, z_dim).cuda()

    style_dict = {}
    style_dict.update(mapping_shape(z_shape))
    style_dict.update(mapping_app(z_app))

    points = rearrange(points, "b Nr Ns c -> b (Nr Ns) c")
    # points = points[:, 0]
    out = net(points, style_dict)

    out.mean().backward()
    pass

  def test__build_NeRFNetwork_SIREN_skip(self, debug=True):
    """
    Usage:

        # export CUDA_VISIBLE_DEVICES=$cuda_devices
        # export RUN_NUM=$run_num

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export PORT=12345
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts root_obs s3://$bucket/ZhouPeng/ \
          --tl_outdir results/train_ffhq_256/train_ffhq_256-20210726_202423_412
          # --tl_outdir results/$resume_dir

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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/nerf_net.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import nerf_net
    from . import multi_head_mapping
    from ..nerf import volume_rendering
    from ..nerf import cam_params

    net = nerf_net.NeRFNetwork_SIREN_skip(**cfg).cuda()

    bs = 4
    H = 64
    W = 64

    cam_param = cam_params.CamParams.from_config(num_imgs=1,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr='axis-angle',
                                                 intr_repr='square',
                                                 initial_fov=53.13,
                                                 freeze_intr=False).cuda()

    intr = cam_param(mode='get_intrinsic')

    rays_o, rays_d, select_inds = cam_param.get_rays_random_pose(
      device='cuda',
      bs=bs,
      intr=intr,
      h_stddev=0.3,
      v_stddev=0.155,
    )

    rays_o = rearrange(rays_o, "b h w c -> b (h w) c", h=H, w=W)
    rays_d = rearrange(rays_d, "b h w c -> b (h w) c", h=H, w=W)

    z_vals, points = volume_rendering.ray_sample_points(rays_o=rays_o,
                                                        rays_d=rays_d,
                                                        near=0.5,
                                                        far=1.5,
                                                        N_samples=24,
                                                        perturb=0)

    print(f"x range: [{points[..., 0].min()}, {points[..., 0].max()}]")
    print(f"y range: [{points[..., 1].min()}, {points[..., 1].max()}]")
    print(f"z range: [{points[..., 2].min()}, {points[..., 2].max()}]")

    z_dim = 128
    style_dim = 128

    mapping_shape = multi_head_mapping.MultiHeadMappingNetwork(z_dim=z_dim,
                                                               hidden_dim=net.shape_net_cfg.style_dim,
                                                               base_layers=4,
                                                               head_layers=0,
                                                               head_dim_dict=net.style_dim_dict_shape,
                                                               add_norm=True,
                                                               norm_out=True).cuda()
    mapping_app = multi_head_mapping.MultiHeadMappingNetwork(z_dim=z_dim,
                                                             hidden_dim=net.app_net_cfg.style_dim,
                                                             base_layers=4,
                                                             head_layers=0,
                                                             head_dim_dict=net.style_dim_dict_app,
                                                             add_norm=True,
                                                             norm_out=True).cuda()

    z_shape = torch.randn(bs, z_dim).cuda()
    z_app = torch.randn(bs, z_dim).cuda()

    style_dict = {}
    style_dict.update(mapping_shape(z_shape))
    style_dict.update(mapping_app(z_app))

    points = rearrange(points, "b Nr Ns c -> b (Nr Ns) c")
    # points = points[:, 0]
    out = net(points, style_dict)

    out.mean().backward()
    pass


