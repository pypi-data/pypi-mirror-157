import pathlib
import os
import sys
import unittest
import argparse


class Testing_MaxToKeep(unittest.TestCase):

  def test_step_and_ret_circle_dir(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    os.environ['PATH'] = f"{os.path.dirname(sys.executable)}:{os.environ['PATH']}"
    os.environ['TORCH_EXTENSIONS_DIR'] = "torch_extensions"

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    PORT = os.environ.get('PORT', 8888)

    from tl2 import tl2_utils

    max2keep = tl2_utils.MaxToKeep.get_named_max_to_keep('test')

    for i in range(20):
      subdir = max2keep.step_and_ret_circle_dir(args.tl_outdir, i)

    pass

