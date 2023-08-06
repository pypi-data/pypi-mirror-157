import os
import sys
import unittest
import argparse


class Testing_open3d_tensorboard(unittest.TestCase):
  
  def test_open3d_tensorbard_web(self, debug=True):
    """
    Usage:

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=0
        export PYTHONPATH=.:./tl2_lib
        python -c "from tl2_lib.tl2.proj.trimesh.examples.open3d.test_open3d_tensorboard import Testing_open3d_tensorboard;\
          Testing_open3d_tensorboard().test_open3d_tensorbard_web(debug=False)"

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
    
    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file tl2_lib/tl2/proj/trimesh/examples/open3d/open3d_tensorboard.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)
    
    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    os.environ['DNNLIB_CACHE_DIR'] = "cache_dnnlib"
    os.environ['TORCH_EXTENSIONS_DIR'] = "cache_torch_extensions"
    os.environ['PATH'] = f"{os.path.dirname(sys.executable)}:{os.environ['PATH']}"
    # os.environ['MESA_GL_VERSION_OVERRIDE'] = "3.30"
    
    import importlib
    
    # script = "tl2_lib/tl2/proj/streamlit/scripts/run_web.py"
    script = importlib.import_module('tl2.proj.streamlit.scripts.run_web').__file__
    if debug:
      cmd_str = f"""
          python
            {script}
            {get_append_cmd_str(args)}
            --tl_debug
            --tl_opts
              """
    else:
      cmd_str_prefix = f"""
              {os.path.dirname(sys.executable)}/streamlit run --server.port {cfg.port}
              {script}
              --
            """
      cmd_str = f"""
          {cmd_str_prefix}
            {get_append_cmd_str(args)}
            --tl_opts {tl_opts}
        """
    start_cmd_run(cmd_str)
    pass

