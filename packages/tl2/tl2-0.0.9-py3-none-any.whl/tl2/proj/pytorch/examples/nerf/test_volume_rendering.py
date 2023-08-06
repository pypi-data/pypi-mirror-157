import os
import sys
import unittest
import argparse


class Testing_volume_rendering(unittest.TestCase):

  def test_ray_sample_points(self, debug=True):
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
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
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

    from . import cam_params
    from . import volume_rendering

    num_imgs = 20
    H = 756
    W = 1008
    N_rays = 1024
    # N_rays = -1
    so3_representation = 'axis-angle'

    cam_param = cam_params.CamParams.from_config(num_imgs=num_imgs,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr=so3_representation,
                                                 intr_repr='square',
                                                 initial_fov=53.13).cuda()

    idx = [0, 1]
    R, t, fx, fy = cam_param(idx)

    rays_o, rays_d, select_inds = cam_params.get_rays(
      rot=R,
      trans=t,
      focal_x=fx,
      focal_y=fy,
      H=H,
      W=W,
      N_rays=N_rays,
      representation=so3_representation)

    near = 0
    far = 1
    N_samples = 128
    batched = True
    lindisp = False
    perturb = 1.

    z_vals, pts =  volume_rendering.ray_sample_points(rays_o=rays_o,
                                                      rays_d=rays_d,
                                                      near=near,
                                                      far=far,
                                                      N_samples=N_samples,
                                                      batched=batched,
                                                      lindisp=lindisp,
                                                      perturb=perturb)


    pass

  def test_ray_integration(self, debug=True):
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
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
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

    import torch
    from . import cam_params
    from . import volume_rendering

    num_imgs = 20
    bs = 2
    H = 756
    W = 1008
    N_rays = 1024
    # N_rays = -1
    so3_representation = 'axis-angle'

    cam_param = cam_params.CamParams.from_config(num_imgs=num_imgs,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr=so3_representation,
                                                 intr_repr='square',
                                                 initial_fov=53.13).cuda()

    idx = list(range(bs))
    R, t, fx, fy = cam_param(idx)

    rays_o, rays_d, select_inds = cam_params.get_rays(
      rot=R,
      trans=t,
      focal_x=fx,
      focal_y=fy,
      H=H,
      W=W,
      N_rays=N_rays,
      representation=so3_representation)

    near = 0
    far = 1
    N_samples = 128
    batched = True
    lindisp = False
    perturb = 1.

    z_vals, pts = volume_rendering.ray_sample_points(rays_o=rays_o,
                                                     rays_d=rays_d,
                                                     near=near,
                                                     far=far,
                                                     N_samples=N_samples,
                                                     batched=batched,
                                                     lindisp=lindisp,
                                                     perturb=perturb)

    raw_rgb = torch.rand(bs, N_rays, N_samples, 3).cuda()
    raw_sigma = torch.rand(bs, N_rays, N_samples).cuda()

    volume_rendering.ray_integration(raw_rgb=raw_rgb,
                                     raw_sigma=raw_sigma,
                                     z_vals=z_vals,
                                     rays_d=rays_d,
                                     raw_noise_std=1.0)

    pass

  def test_sample_pdf(self, debug=True):
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
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
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

    import torch
    from . import cam_params
    from . import volume_rendering

    num_imgs = 20
    bs = 2
    H = 756
    W = 1008
    N_rays = 1024
    # N_rays = -1
    so3_representation = 'axis-angle'

    cam_param = cam_params.CamParams.from_config(num_imgs=num_imgs,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr=so3_representation,
                                                 intr_repr='square',
                                                 initial_fov=53.13).cuda()

    idx = list(range(bs))
    R, t, fx, fy = cam_param(idx)

    rays_o, rays_d, select_inds = cam_params.get_rays(
      rot=R,
      trans=t,
      focal_x=fx,
      focal_y=fy,
      H=H,
      W=W,
      N_rays=N_rays,
      representation=so3_representation)

    near = 0
    far = 1
    N_samples = 128
    batched = True
    lindisp = False
    # perturb = 1.
    perturb = 0.

    z_vals, pts = volume_rendering.ray_sample_points(rays_o=rays_o,
                                                     rays_d=rays_d,
                                                     near=near,
                                                     far=far,
                                                     N_samples=N_samples,
                                                     batched=batched,
                                                     lindisp=lindisp,
                                                     perturb=perturb)

    raw_rgb = torch.rand(bs, N_rays, N_samples, 3).cuda()
    raw_sigma = torch.rand(bs, N_rays, N_samples).cuda()

    *_, weights = volume_rendering.ray_integration(raw_rgb=raw_rgb,
                                                   raw_sigma=raw_sigma,
                                                   z_vals=z_vals,
                                                   rays_d=rays_d,
                                                   raw_noise_std=1.0)

    z_vals_mid = 0.5 * (z_vals[..., 1:] + z_vals[..., :-1])
    samples = volume_rendering.sample_pdf(bins=z_vals_mid,
                                          weights=weights[..., 1:-1],
                                          N_importance=N_samples,
                                          det=(perturb == 0.))

    pass