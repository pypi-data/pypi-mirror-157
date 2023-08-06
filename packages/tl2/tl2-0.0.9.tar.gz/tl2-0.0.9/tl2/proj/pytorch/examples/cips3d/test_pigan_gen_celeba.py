import os
import sys
import unittest

import torch


class Testing_pigan_gen_celeba(unittest.TestCase):

  def test__build_generator(self, debug=True):
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/cips3d/pigan_gen_celeba.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts} 
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    os.environ['DNNLIB_CACHE_DIR'] = "cache_dnnlib"
    os.environ['TORCH_EXTENSIONS_DIR'] = "cache_torch_extensions"
    os.environ['PATH'] = f"{os.path.dirname(sys.executable)}:{os.environ['PATH']}"
    os.environ['MAX_JOBS '] = "8"

    from torchvision.utils import make_grid
    import torchvision.transforms.functional as tv_f
    from tl2.proj.fvcore import build_model, TLCfgNode
    from tl2.proj.fvcore.checkpoint import Checkpointer
    from tl2.proj.pil import pil_utils
    from tl2.proj.pytorch import torch_utils
    from tl2.proj.pytorch.examples.nerf import cam_params_pigan
    from tl2.proj.pytorch.examples.cips3d.pigan_gen_celeba import Generator_Diffcam

    torch_utils.init_seeds(seed=0)

    device = 'cuda'

    # G = build_model(cfg.G_cfg).to(device)
    # Checkpointer(G).load_state_dict_from_file(cfg.network_pkl)

    metadata = cfg.G_kwargs
    metadata['nerf_kwargs']['h_stddev'] = 0.
    metadata['nerf_kwargs']['v_stddev'] = 0.

    num_imgs = 2
    H = W = 64
    # N_rays = 1024
    N_rays = -1

    # ckpt_dir = "../bucket_3690/results/CIPS-3D/ffhq_diffcam_exp_v4/train_ffhq-20220225_164209_334/ckptdir/resume"
    ckpt_dir = None

    if ckpt_dir is not None:
      load_G_cfg = TLCfgNode.load_yaml_file(cfg_filename=f"{os.path.abspath(ckpt_dir)}/config_command.yaml")
      load_G_cfg = list(load_G_cfg.values())[0]

    else:
      load_G_cfg = cfg
      D = None
    G = Generator_Diffcam(**load_G_cfg.G_cfg).to(device)

    pigan_mapping_pkl = 'cache_pretrained/pretrained/CelebA/G_ema_celeba_converted_mapping.pth'
    Checkpointer(G.mapping_shape_app).load_state_dict_from_file(pigan_mapping_pkl)

    pigan_nerf_pkl = 'cache_pretrained/pretrained/CelebA/G_ema_celeba_converted_nerf.pth'
    Checkpointer(G.nerf_net).load_state_dict_from_file(pigan_nerf_pkl)

    torch.save(G.state_dict(), 'cache_pretrained/pretrained/CelebA/G_ema_celeba_converted_all.pth')

    cam_param = cam_params_pigan.CamParams.from_config(H0=H, W0=W, **load_G_cfg.get('cam_cfg', {})).cuda()

    if ckpt_dir is not None:
      model_dict = {
        # 'G_ema': G,
        'generator': G,
        'cam_param': cam_param
      }
      torch_utils.load_models(ckpt_dir, model_dict=model_dict)

    intr = cam_param(mode='get_intrinsic')
    rays_o, rays_d, select_inds = cam_param.get_rays_random_pose(
      device=device, bs=num_imgs, intr=intr, **metadata.nerf_kwargs)

    G.eval()
    zs = G.get_zs(num_imgs)

    with torch.set_grad_enabled(True):
      imgs, ret_imgs = G(zs=zs,
                         rays_o=rays_o,
                         rays_d=rays_d,
                         forward_points=256 ** 2,  # disable gradients
                         return_aux_img=True,
                         **{**metadata,
                            'psi': 0.})

      g_imgs_aux = ret_imgs['aux_img']
      gen_imgs = torch.cat([imgs, g_imgs_aux], dim=0)

    img = make_grid(gen_imgs, nrow=num_imgs, normalize=True, scale_each=True)
    img_pil = tv_f.to_pil_image(img)
    pil_utils.imshow_pil(img_pil, f"whole {imgs.shape}")

    pass