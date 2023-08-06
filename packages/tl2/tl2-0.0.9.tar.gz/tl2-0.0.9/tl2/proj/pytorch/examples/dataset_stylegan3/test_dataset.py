import os
import sys
import unittest
import argparse


class Testing_dataset(unittest.TestCase):

  def test_build_ImageFolderDataset(self, debug=True):
    """
    Dataset input: 3dmm_210;

    Usage:

        # export CUDA_VISIBLE_DEVICES=$cuda_devices
        # export RUN_NUM=$run_num

        export CUDA_VISIBLE_DEVICES=0,1
        export TIME_STR=0
        export PYTHONPATH=.:./tl2_lib:./stylegan3_lib
        python -c "from exp.tests.test_encoder_inr import Testing_encoder_inr_train_v2;\
          Testing_encoder_inr_train_v2().test_train_ffhq_r256_softplus(debug=False)" \
          --tl_mox True \
          --tl_opts root_obs s3://bucket-3690/ZhouPeng \
            data_cfg.max_size None use_input_dataset True \
            loss_cfg.mse_gamma 0. gamma 10. eval_fid_num_gen_images 2048 \
            data datasets/ffhq/downsample_ffhq_256x256.zip resolution 64 \
            batch 32 tick 1 snap 4 D_reg_interval 1 \
            reset_worst_fid False \
          --tl_outdir

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
      # resume_dir = "/home/ma-user/work/ZhouPeng/results/stylegan3-exp/encoder_inr_train/train_ffhq_r256_diffaug-20211216_203318_145"
      # sys.argv.extend(['--tl_outdir', resume_dir])
      pass
    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    resume = os.path.isdir(f"{outdir}/ckptdir/resume") and \
             tl2_utils.parser_args_from_list(name="--tl_outdir", argv_list=sys.argv, type='str') is not None
    argv_str = f"""
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/dataset_stylegan3/dataset.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    if int(os.environ['RUN_NUM']) > 0:
      run_command = f"""
                  python -c "from tl2.modelarts.tests.test_run import TestingRun;\
                        TestingRun().test_run_v2(number={os.environ['RUN_NUM']}, )" \
                        --tl_opts root_obs {cfg.root_obs}
                  """
      p = tl2_utils.Worker(name='Run', args=(run_command,))
      p.start()

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    PORT = os.environ.get('PORT', 8888)

    os.environ['DNNLIB_CACHE_DIR'] = "cache_dnnlib"
    os.environ['TORCH_EXTENSIONS_DIR'] = "cache_torch_extensions"
    os.environ['PATH'] = f"{os.path.dirname(sys.executable)}:{os.environ['PATH']}"

    import torch
    from tl2.proj.fvcore import build_model
    from .dataset import get_training_dataloader


    dataset = build_model(cfg.data_cfg)
    data = dataset[0]

    rank = 0
    num_gpus = 1
    batch_size = 4
    num_workers = 0

    data_loader = get_training_dataloader(dataset=dataset, rank=rank, num_gpus=num_gpus,
                                          batch_size=batch_size, num_workers=num_workers,
                                          **cfg.data_loader_cfg)

    data_loader_iter = iter(data_loader)

    data = next(data_loader_iter)

    pass

  def test_build_dataloader_ddp(self, debug=True):
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
      os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
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
                --tl_config_file tl2_lib/tl2/proj/pytorch/examples/dataset_stylegan3/dataset.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                {"--tl_resume --tl_resumedir " + outdir if resume else ""}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    if int(os.environ['RUN_NUM']) > 0:
      run_command = f"""
                  python -c "from tl2.modelarts.tests.test_run import TestingRun;\
                        TestingRun().test_run_v2(number={os.environ['RUN_NUM']}, )" \
                        --tl_opts root_obs {cfg.root_obs}
                  """
      p = tl2_utils.Worker(name='Run', args=(run_command,))
      p.start()

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    PORT = os.environ.get('PORT', 12345)

    # if 'CUDA_HOME' not in os.environ: os.environ['CUDA_HOME'] = "/usr/local/cuda-10.2/"
    # os.environ['PATH'] = f"{os.path.dirname(sys.executable)}:{os.environ['PATH']}"
    # os.environ['DNNLIB_CACHE_DIR'] = "datasets/pretrained"
    # os.environ['TORCH_EXTENSIONS_DIR'] = "torch_extensions"

    cmd_str = f"""
        python -m torch.distributed.launch --nproc_per_node={n_gpus} --master_port={PORT} 
        tl2_lib/tl2/proj/pytorch/examples/dataset_stylegan3/test_ddp.py
        {get_append_cmd_str(args)}
        """
    if debug:
      cmd_str += f"""
                  --tl_debug
                  --tl_opts 
                  """
    else:
      cmd_str += f"""
                  --num_workers {n_gpus}
                  --tl_opts {tl_opts}
                  """
    start_cmd_run(cmd_str)
    # from tl2.launch.launch_utils import update_parser_defaults_from_yaml, global_cfg
    # from tl2.modelarts import modelarts_utils
    # update_parser_defaults_from_yaml(parser)

    # modelarts_utils.setup_tl_outdir_obs(global_cfg)
    # modelarts_utils.modelarts_sync_results_dir(global_cfg, join=True)
    # modelarts_utils.prepare_dataset(global_cfg.get('modelarts_download', {}), global_cfg=global_cfg)
    #
    # modelarts_utils.prepare_dataset(global_cfg.get('modelarts_upload', {}), global_cfg=global_cfg, download=False)
    # modelarts_utils.modelarts_sync_results_dir(global_cfg, join=True)
    pass

