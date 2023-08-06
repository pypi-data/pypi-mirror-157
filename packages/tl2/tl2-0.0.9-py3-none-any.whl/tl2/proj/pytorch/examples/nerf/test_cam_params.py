import os
import sys
import unittest
import argparse

from einops import rearrange


class Testing_cam_params(unittest.TestCase):

  def test_CamParams_from_config(self, debug=True):
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

    cam_param = cam_params.CamParams.from_config(num_imgs=20,
                                                 H0=756,
                                                 W0=1008,
                                                 so3_repr='axis-angle',
                                                 intr_repr='square',
                                                 initial_fov=53.13)

    R, t, fx, fy = cam_param(0)

    pass

  def test_get_rays(self, debug=True):
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

    cam_param = cam_params.CamParams.from_config(num_imgs=20,
                                                 H0=756,
                                                 W0=1008,
                                                 so3_repr='axis-angle',
                                                 intr_repr='square',
                                                 initial_fov=53.13).cuda()

    idx = [0, 1]
    R, t, fx, fy = cam_param(idx)

    H = 756
    W = 1008
    N_rays = 1024
    # N_rays = -1
    so3_representation = 'axis-angle'

    rays_o, rays_d, select_inds = cam_params.get_rays(
      rot=R,
      trans=t,
      focal_x=fx,
      focal_y=fy,
      H=H,
      W=W,
      N_rays=N_rays,
      representation=so3_representation)

    c2ws = cam_param.get_camera2worlds().data.cpu().numpy()

    intr = cam_param.get_intrinsic(H, W).data.cpu().numpy()

    pass

  def test_get_rays_by_intr_and_extr(self, debug=True):
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

    num_imgs = 4
    H = 756
    W = 1008
    # N_rays = 1024
    N_rays = -1
    so3_representation = 'axis-angle'

    cam_param = cam_params.CamParams.from_config(num_imgs=num_imgs,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr='axis-angle',
                                                 intr_repr='square',
                                                 initial_fov=53.13).cuda()

    idx = list(range(num_imgs))
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


    c2ws = cam_param.get_camera2worlds()
    intr = cam_param.get_intrinsic(H, W)

    rays_o1, rays_d1, select_inds1 = cam_params.get_rays_by_intr_and_extr(intrinsics=intr,
                                                                          c2w=c2ws,
                                                                          H=H,
                                                                          W=W,
                                                                          N_rays=N_rays)

    assert (rays_o - rays_o1).sum() < 1e-6
    assert (rays_d - rays_d1).sum() < 1e-6
    assert (select_inds == select_inds1).all()

    pass

  def test_get_pose_avg(self, debug=True):
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

    num_imgs = 4
    H = 756
    W = 1008
    # N_rays = 1024
    N_rays = -1
    so3_representation = 'axis-angle'

    cam_param = cam_params.CamParams.from_config(num_imgs=num_imgs,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr='axis-angle',
                                                 intr_repr='square',
                                                 initial_fov=53.13).cuda()



    # c2ws = cam_param.get_camera2worlds()
    intr = cam_param.get_intrinsic(H, W)
    c2ws = cam_param.poses_avg()[None, ...]

    rays_o1, rays_d1, select_inds1 = cam_params.get_rays_by_intr_and_extr(intrinsics=intr,
                                                                          c2w=c2ws,
                                                                          H=H,
                                                                          W=W,
                                                                          N_rays=N_rays)



    pass

  def test_get_rays_random_pose(self, debug=True):
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

    from . import volume_rendering
    from . import cam_params

    num_imgs = 4
    H = 756
    W = 1008
    # N_rays = 1024
    N_rays = -1
    so3_representation = 'axis-angle'

    cam_param = cam_params.CamParams.from_config(num_imgs=num_imgs,
                                                 H0=H,
                                                 W0=W,
                                                 so3_repr='axis-angle',
                                                 intr_repr='square',
                                                 initial_fov=53.13,
                                                 freeze_intr=True).cuda()

    intr = cam_param(mode='get_intrinsic')

    rays_o, rays_d, select_inds = cam_param.get_rays_random_pose(
        device='cuda',
        bs=num_imgs,
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
    pass


class Testing_cam_params_v1(unittest.TestCase):

    def test_get_rays_random_pose(self, debug=True):
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

        from . import volume_rendering
        from . import cam_params_v1

        num_imgs = 4
        H = 756
        W = 1008
        # N_rays = 1024
        N_rays = -1
        so3_representation = 'axis-angle'

        cam_param = cam_params_v1.CamParams.from_config(num_imgs=num_imgs,
                                                        initial_fov=12,
                                                        H0=H,
                                                        W0=W,
                                                        so3_repr='axis-angle',
                                                        intr_repr='square',
                                                        freeze_intr=True).cuda()

        intr = cam_param(mode='get_intrinsic')

        rays_o, rays_d, select_inds = cam_param.get_rays_random_pose(
            device='cuda',
            bs=num_imgs,
            intr=intr,
            h_stddev=0,
            v_stddev=0,)

        rays_o = rearrange(rays_o, "b h w c -> b (h w) c", h=H, w=W)
        rays_d = rearrange(rays_d, "b h w c -> b (h w) c", h=H, w=W)

        z_vals, points = volume_rendering.ray_sample_points(rays_o=rays_o,
                                                            rays_d=rays_d,
                                                            near=0.88,
                                                            far=1.12,
                                                            N_samples=24,
                                                            perturb=0)

        pass


