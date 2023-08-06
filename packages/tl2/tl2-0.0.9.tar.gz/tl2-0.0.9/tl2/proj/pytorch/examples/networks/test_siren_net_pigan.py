import collections
import math
import os
import pprint
import sys
import unittest
import argparse
from einops import rearrange
from itertools import chain

import torch

from tl2.proj.pytorch.pytorch_hook import VerboseModel
from tl2.proj.pytorch import torch_utils
from tl2.proj.pil import pil_utils
from tl2.proj.fvcore.checkpoint import Checkpointer
from tl2.proj.fvcore import TLCfgNode


class Testing_siren_net_pigan(unittest.TestCase):

  def test__build_ShapeNet(self, debug=True):
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/siren_net_pigan.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.pytorch_hook import VerboseModel
    from tl2.proj.pytorch.examples.networks import multi_head_mapping
    from tl2.proj.pytorch.examples.networks import siren_net_pigan

    net = siren_net_pigan.ShapeNet(**cfg.shape_cfg).cuda()
    head_dim_dict = net.style_dim_dict
    mapping_net = multi_head_mapping.MultiHeadMappingNetwork(head_dim_dict=head_dim_dict, **cfg.mapping_cfg).cuda()

    bs = 4
    N = 10
    in_dim = cfg.shape_cfg.input_dim

    z = torch.randn(bs, cfg.mapping_cfg.z_dim).cuda()
    style_dict = mapping_net(z)

    x = torch.randn(bs, N, in_dim).cuda()

    out = net(x, style_dict=style_dict)

    VerboseModel.forward_verbose(mapping_net,
                                 inputs_args=(z,),
                                 name_prefix='mapping.',
                                 )

    pass

  def test__build_AppNet(self, debug=True):
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/siren_net_pigan.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.pytorch_hook import VerboseModel
    from tl2.proj.pytorch.examples.networks import multi_head_mapping
    from tl2.proj.pytorch.examples.networks import siren_net_pigan

    net = siren_net_pigan.AppNet(**cfg.shape_cfg).cuda()
    head_dim_dict = net.style_dim_dict
    mapping_net = multi_head_mapping.MultiHeadMappingNetwork(head_dim_dict=head_dim_dict, **cfg.mapping_cfg).cuda()

    bs = 4
    N = 10
    in_dim = cfg.shape_cfg.input_dim

    z = torch.randn(bs, cfg.mapping_cfg.z_dim).cuda()
    style_dict = mapping_net(z)

    x = torch.randn(bs, N, in_dim).cuda()

    out = net(x, style_dict=style_dict)

    VerboseModel.forward_verbose(mapping_net,
                                 inputs_args=(z,),
                                 name_prefix='mapping.',
                                 )

    pass

  def test__build_siren(self, debug=True):
    """
    pigan nerf network on celeba;
    save kwargs and out;

    Usage:

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=.:./tl2_lib:./piGAN_lib
        python -c "from exp.tests.test_pigan import Testing_pretrained;\
          Testing_pretrained().test_inverse_render_web(debug=False)" \
          --tl_opts port 8591

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    yaml_file = 'exp/pigan/configs/pretrained.yaml'
    cfg = TLCfgNode.load_yaml_with_command(yaml_file, command='_build_generator_CelebA')

    import torch
    from tl2.proj.pytorch.pytorch_hook import VerboseModel
    from exp.pigan import pigan_utils
    from exp.comm.pigan import network

    device = torch.device('cuda')

    model_pkl = 'cache_pretrained/pretrained/CelebA/generator.pth'
    G_ema = pigan_utils.load_generator_ema(model_pkl)
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba.pth"
    torch.save(G_ema.state_dict(), saved_pkl)

    G_kwargs = cfg.G_kwargs
    G_kwargs.h_mean = eval(G_kwargs.h_mean)
    G_kwargs.v_mean = eval(G_kwargs.v_mean)

    del G_ema
    G_ema = network.ImplicitGenerator3d(device=device, **G_kwargs)
    Checkpointer(G_ema).load_state_dict_from_file(saved_pkl)

    loaded_kwargs = torch.load("datasets/kwargs/forward_with_frequencies_phase_shifts.pth")

    with torch.no_grad():
      out = G_ema.siren.forward_with_frequencies_phase_shifts(**loaded_kwargs)
      rgb = out[:, :, :3]
      sigma = out[:, :, 3:]
      saved_data = {
        'rgb': rgb,
        'sigma': sigma,
      }
      torch.save(saved_data, "datasets/kwargs/forward_with_frequencies_phase_shifts_out.pth")


    pass

  def test__build_mapping_pigan(self, debug=True):
    """
    Usage:

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=.:./tl2_lib:./piGAN_lib
        python -c "from exp.tests.test_pigan import Testing_pretrained;\
          Testing_pretrained().test_inverse_render_web(debug=False)" \
          --tl_opts port 8591

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    yaml_file = 'exp/pigan/configs/pretrained.yaml'
    cfg = TLCfgNode.load_yaml_with_command(yaml_file, command='_build_generator_CelebA')

    import torch
    from tl2.proj.pytorch.pytorch_hook import VerboseModel
    from exp.pigan import pigan_utils
    from exp.comm.pigan import network

    device = torch.device('cuda')
    torch_utils.init_seeds(seed=0)

    model_pkl = 'cache_pretrained/pretrained/CelebA/generator.pth'
    G_ema = pigan_utils.load_generator_ema(model_pkl)
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba.pth"
    torch.save(G_ema.state_dict(), saved_pkl)

    G_kwargs = cfg.G_kwargs
    G_kwargs.h_mean = eval(G_kwargs.h_mean)
    G_kwargs.v_mean = eval(G_kwargs.v_mean)

    del G_ema
    G_ema = network.ImplicitGenerator3d(device=device, **G_kwargs)
    Checkpointer(G_ema).load_state_dict_from_file(saved_pkl)

    z = torch.randn((10000, 256), device=device)
    with torch.no_grad():
      VerboseModel.forward_verbose(G_ema.siren.mapping_network,
                                   inputs_args=(z,),
                                   submodels=['network'],
                                   name_prefix='mapping.')
      frequencies, phase_shifts = G_ema.siren.mapping_network(z)

      saved_dict = {
        'z': z,
        'frequencies': frequencies,
        'phase_shifts': phase_shifts,
      }
      torch.save(saved_dict, "datasets/kwargs/mapping_network_kwargs_out.pth")

    w_frequencies = frequencies.mean(0, keepdim=True)
    w_phase_shifts = phase_shifts.mean(0, keepdim=True)

    pass

  def test__build_generator_CelebA(self, debug=True):
    """
    Usage:

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=.:./tl2_lib:./piGAN_lib
        python -c "from exp.tests.test_pigan import Testing_pretrained;\
          Testing_pretrained().test_inverse_render_web(debug=False)" \
          --tl_opts port 8591

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    yaml_file = 'exp/pigan/configs/pretrained.yaml'
    cfg = TLCfgNode.load_yaml_with_command(yaml_file, command='_build_generator_CelebA')

    import torch
    from tl2.proj.pytorch.pytorch_hook import VerboseModel
    from exp.pigan import pigan_utils
    from exp.comm.pigan import network

    device = torch.device('cuda')

    model_pkl = 'cache_pretrained/pretrained/CelebA/generator.pth'
    G_ema = pigan_utils.load_generator_ema(model_pkl)
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba.pth"
    torch.save(G_ema.state_dict(), saved_pkl)

    G_kwargs = cfg.G_kwargs
    G_kwargs.h_mean = eval(G_kwargs.h_mean)
    G_kwargs.v_mean = eval(G_kwargs.v_mean)

    del G_ema
    G_ema = network.ImplicitGenerator3d(device=device, **G_kwargs)
    Checkpointer(G_ema).load_state_dict_from_file(saved_pkl)

    z = torch.randn((10000, 256), device=device)
    with torch.no_grad():
      VerboseModel.forward_verbose(G_ema.siren.mapping_network,
                                   inputs_args=(z,),
                                   submodels=['network'],
                                   name_prefix='mapping.')
      frequencies, phase_shifts = G_ema.siren.mapping_network(z)

    w_frequencies = frequencies.mean(0, keepdim=True)
    w_phase_shifts = phase_shifts.mean(0, keepdim=True)
    with torch.no_grad():
      frame, _ = G_ema.forward_with_frequencies(w_frequencies, w_phase_shifts, **G_kwargs)
      frame_pil = torch_utils.img_tensor_to_pil(frame)
      pil_utils.imshow_pil(frame_pil, frame.shape)

    pass

  def test__build_NeRF_Net_kwargs(self, debug=True):
    """
    Convert pigan nerf weights;

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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/siren_net_pigan.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import siren_net_pigan
    from . import multi_head_mapping
    from ..nerf import volume_rendering
    from ..nerf import cam_params

    net = siren_net_pigan.NeRF_Net(**cfg).cuda()

    loaded_kwargs = torch.load("datasets/kwargs/forward_with_frequencies_phase_shifts.pth")
    # kwargs_saved = {
    #     'input': input,
    #     'frequencies': frequencies,
    #     'phase_shifts': phase_shifts,
    #     'ray_directions': ray_directions,
    # }
    points = loaded_kwargs['input']
    ray_directions = loaded_kwargs['ray_directions']
    frequencies = loaded_kwargs['frequencies']
    phase_shifts = loaded_kwargs['phase_shifts']

    style_dict = net.parse_style_dict(frequencies=frequencies, phase_shifts=phase_shifts)

    # convert weights of pigan
    model_pkl = 'cache_pretrained/pretrained/CelebA/generator.pth'
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba.pth"
    loaded_state_dict = torch.load(saved_pkl)

    state_dict = collections.OrderedDict()
    weights_list = list(loaded_state_dict.values())
    for idx, name in enumerate(net.state_dict().keys()):
      state_dict[name] = weights_list[idx]
    Checkpointer(net).load_state_dict(state_dict)

    # save converted weights
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba_converted_nerf.pth"
    torch.save(net.state_dict(), saved_pkl)

    # check out
    Checkpointer(net).load_state_dict_from_file(saved_pkl)
    fea, rgb, sigma = net(x=points, style_dict=style_dict, ray_directions=ray_directions)

    loaded_data = torch.load("datasets/kwargs/forward_with_frequencies_phase_shifts_out.pth")
    loaded_rgb = loaded_data['rgb']
    loaded_sigma = loaded_data['sigma']

    err_rgb = (loaded_rgb - rgb).abs().sum()
    err_sigma = (loaded_sigma - sigma).abs().sum()

    # out.mean().backward()
    pass

  def test__build_MappingNetwork(self, debug=True):
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/siren_net_pigan.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import siren_net_pigan
    from . import multi_head_mapping
    from ..nerf import volume_rendering
    from ..nerf import cam_params

    net = siren_net_pigan.MappingNetwork(**cfg).cuda()

    model_pkl = 'cache_pretrained/pretrained/CelebA/generator.pth'
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba.pth"
    loaded_state_dict = torch.load(saved_pkl)
    weights_list = []
    for name, weights in loaded_state_dict.items():
      if 'mapping_network' in name:
        weights_list.append(weights)

    state_dict = collections.OrderedDict()
    for idx, name in enumerate(net.state_dict().keys()):
      state_dict[name] = weights_list[idx]
    Checkpointer(net).load_state_dict(state_dict)

    # save converted weights
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba_converted_mapping.pth"
    torch.save(net.state_dict(), saved_pkl)

    pass

  def test__build_StyleMappingBaseNet(self, debug=True):
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/siren_net_pigan.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import siren_net_pigan

    net = siren_net_pigan.StyleMappingBaseNet(**cfg).cuda()

    bs = 4
    z_dim = cfg.z_dim
    z = torch.randn(bs, z_dim).cuda()

    out = net(z)

    pass

  def test__build_StyleMappingShapeApp(self, debug=True):
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/siren_net_pigan.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import siren_net_pigan
    from . import multi_head_mapping
    from ..nerf import volume_rendering
    from ..nerf import cam_params

    nerf_net = siren_net_pigan.NeRF_Net(**cfg.nerf_cfg).cuda()

    mapping_net = siren_net_pigan.StyleMappingShapeApp(**cfg.mapping_cfg,
                                                       style_dim_dict_shape=nerf_net.style_dim_dict_shape,
                                                       style_dim_dict_app=nerf_net.style_dim_dict_app).cuda()

    bs = 4
    z_dim = mapping_net.z_dim
    z_shape = torch.randn(bs, z_dim).cuda()
    z_app = torch.randn(bs, z_dim).cuda()

    style_dict = mapping_net(z_shape=z_shape, z_app=z_app)

    mapping_net_state_dict = mapping_net.state_dict()
    pprint.pprint(list(mapping_net_state_dict.keys()))

    # convert pigan weights
    model_pkl = 'cache_pretrained/pretrained/CelebA/generator.pth'
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba.pth"
    loaded_state_dict = torch.load(saved_pkl)
    loaded_mapping_weights_list = []
    for name, weights in loaded_state_dict.items():
      if 'mapping_network' in name:
        loaded_mapping_weights_list.append(weights)

    # base_net weights
    state_list = loaded_mapping_weights_list[:-2]

    # heads
    heads_weights = loaded_mapping_weights_list[-2]
    heads_bias = loaded_mapping_weights_list[-1]

    heads_weights_freq, heads_weights_phase = heads_weights.chunk(2, dim=0)
    heads_bias_freq, heads_bias_phase = heads_bias.chunk(2, dim=0)

    weights_dict = nerf_net.parse_weight_dict(frequencies=heads_weights_freq, phase_shifts=heads_weights_phase)
    bias_dict = nerf_net.parse_weight_dict(frequencies=heads_bias_freq, phase_shifts=heads_bias_phase)
    for _weight, _bias in zip(weights_dict.values(), bias_dict.values()):
      state_list.append(_weight)
      state_list.append(_bias)
    assert len(state_list) == len(mapping_net_state_dict)

    state_dict = collections.OrderedDict()
    for idx, (name, _) in enumerate(mapping_net_state_dict.items()):
      state_dict[name] = state_list[idx]

    Checkpointer(mapping_net).load_state_dict(state_dict)
    # save converted weights
    saved_pkl = f"{os.path.dirname(model_pkl)}/G_ema_celeba_converted_mapping.pth"
    torch.save(mapping_net.state_dict(), saved_pkl)

    # check out
    loaded_kwargs = torch.load("datasets/kwargs/mapping_network_kwargs_out.pth")
    z_shape = loaded_kwargs['z']
    frequencies = loaded_kwargs['frequencies']
    phase_shifts = loaded_kwargs['phase_shifts']
    loaded_style_dict = nerf_net.parse_style_dict(frequencies=frequencies, phase_shifts=phase_shifts)

    Checkpointer(mapping_net).load_state_dict_from_file(saved_pkl)
    style_dict = mapping_net(z_shape=z_shape, z_app=z_shape)
    for name in style_dict.keys():
      assert (style_dict[name] - loaded_style_dict[name]).abs().sum() == 0, name

    pass

  def test__build_NeRF_Net(self, debug=True):
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/networks/siren_net_pigan.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                --tl_debug True
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    from tl2.proj.pytorch.examples.networks import siren_net_pigan
    from . import multi_head_mapping
    from ..nerf import volume_rendering
    from ..nerf import cam_params

    net = siren_net_pigan.NeRF_Net(**cfg).cuda()

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
