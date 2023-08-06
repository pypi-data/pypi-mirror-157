import os
import sys
import unittest
import argparse


class Testing_dataset_tool(unittest.TestCase):

  def test_FFHQ_1024_to_256(self, debug=True):
    """
    Usage:
        ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=2 root@localhost -p 2232

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=0
        export PYTHONPATH=.:tl2_lib
        python -c "from tl2_lib.tl2.tools.test_tools import Testing_dataset_tool;\
          Testing_dataset_tool().test_FFHQ_1024_to_256(debug=False)"

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                """
    args = setup_outdir_and_yaml(argv_str)

    tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    print(f'tl_opts:\n {tl_opts}')

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    cmd_str = f"""
        python 
        tl2_lib/tl2/tools/dataset_tool.py
        --source=datasets/ffhq/images1024x1024
        --dest=datasets/ffhq/downsample_ffhq_256x256.zip
        --width=256 --height=256
        {get_append_cmd_str(args)}
        """
    if debug:
      cmd_str = f"""
              python 
              tl2_lib/tl2/tools/dataset_tool.py
              --source=datasets/ffhq/images1024x1024
              --dest=datasets/ffhq/downsample_ffhq_256x256_debug.zip
              --width=256 --height=256
              --tl_debug
              {get_append_cmd_str(args)}
              """
    # else:
    #   cmd_str += f"""
    #               {get_append_cmd_str(args)}
    #               --tl_opts {tl_opts}
    #               """
    start_cmd_run(cmd_str)
    pass

