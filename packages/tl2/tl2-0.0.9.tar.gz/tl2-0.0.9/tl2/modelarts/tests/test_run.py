import os
import sys
import unittest
import argparse


class TestingRun(unittest.TestCase):

  def test_run(self, *tmp):
    """
    Usage:
        export ANSI_COLORS_DISABLED=1
        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=./
        python template_lib/modelarts/scripts/run.py \
          --tl_config_file template_lib/modelarts/tests/configs/run.yaml \
          --tl_command run \
          --tl_outdir results/Run/run \
          --number 1

        # default image
        /bucket-8280/ZhouPeng/codes/Omni-GAN-ImageNet/template_lib/modelarts/scripts/run.py
          number = 3
          tl_outdir = results/Run/run
          tl_config_file = template_lib/modelarts/tests/configs/run.yaml
          tl_opts = root_obs s3://bucket-7001/ZhouPeng/
          tl_command = run

        # self defined image
        bash /home/work/run_train.sh python /home/work/user-job-dir/Omni-GAN-ImageNet/template_lib/modelarts/scripts/run.py --tl_outdir=results/Run/run --tl_config_file=/home/work/user-job-dir/Omni-GAN-ImageNet/template_lib/modelarts/tests/configs/run.yaml --tl_command=run --tl_opts=root_obs s3://bucket-7001/ZhouPeng/ --number=2
    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    # if 'TIME_STR' not in os.environ:
    #   os.environ['TIME_STR'] = '0' if utils.is_debugging() else '0'
    os.environ['TIME_STR'] = '0'
    if 'RESULTS_OBS' not in os.environ:
      os.environ['RESULTS_OBS'] = 's3://bucket-xx/ZhouPeng/results'
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                    --tl_config_file tl2_lib/tl2/modelarts/configs/run.yaml
                    --tl_command {command}
                    --tl_outdir {outdir}
                    """
    args = setup_outdir_and_yaml(argv_str)

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    cmd_str = f"""
            python tl2_lib/tl2/modelarts/scripts/run.py
            {get_append_cmd_str(args)}
            --number 1
            """
    start_cmd_run(cmd_str)

    pass

  def test_run_v2(self, number=1, debug=False, **kwargs):
    """
    Usage:
        export ANSI_COLORS_DISABLED=1
        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=./
        python template_lib/modelarts/scripts/run.py \
          --tl_config_file template_lib/modelarts/tests/configs/run.yaml \
          --tl_command run \
          --tl_outdir results/Run/run \
          --number 1

        # default image
        /bucket-8280/ZhouPeng/codes/Omni-GAN-ImageNet/template_lib/modelarts/scripts/run.py
          number = 3
          tl_outdir = results/Run/run
          tl_config_file = template_lib/modelarts/tests/configs/run.yaml
          tl_opts = root_obs s3://bucket-7001/ZhouPeng/
          tl_command = run

        # self defined image
        bash /home/work/run_train.sh python /home/work/user-job-dir/Omni-GAN-ImageNet/template_lib/modelarts/scripts/run.py --tl_outdir=results/Run/run --tl_config_file=/home/work/user-job-dir/Omni-GAN-ImageNet/template_lib/modelarts/tests/configs/run.yaml --tl_command=run --tl_opts=root_obs s3://bucket-7001/ZhouPeng/ --number=2
    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
    # if 'TIME_STR' not in os.environ:
    #   os.environ['TIME_STR'] = '0' if utils.is_debugging() else '0'
    os.environ['TIME_STR'] = '1'
    # if 'RESULTS_OBS' not in os.environ:
    #   os.environ['RESULTS_OBS'] = 's3://bucket-xx/ZhouPeng/results'
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
                    --tl_config_file tl2_lib/tl2/modelarts/configs/run.yaml
                    --tl_command {command}
                    --tl_outdir {outdir}
                    --tl_opts {tl_opts}
                    """
    args = setup_outdir_and_yaml(argv_str)

    os.environ['TIME_STR'] = '0'
    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    cmd_str = f"""
            python tl2_lib/tl2/modelarts/scripts/run.py
            {get_append_cmd_str(args)}
            --number {number}
            --tl_opts {tl_opts}
            """
    start_cmd_run(cmd_str)

    pass

  def test_run_v2_modelarts(self, debug=True):
    """
    Usage:

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export PORT=12345
        export TIME_STR=1
        export RUN_NUM=0
        export PYTHONPATH=.
        python -c "from tl2_lib.tl2.modelarts.tests.test_run import TestingRun;\
          TestingRun().test_run_v2_modelarts(debug=False)" \
          --tl_opts root_obs s3://$bucket/ZhouPeng/ \
          --tl_outdir results/train_ffhq_256/train_ffhq_256-20210726_202423_412

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
                --tl_config_file tl2_lib/tl2/modelarts/configs/run.yaml
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

    cmd_str = f"""
        python -m tl2.modelarts.scripts.test_bash {os.environ['CUDA_VISIBLE_DEVICES']}
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
