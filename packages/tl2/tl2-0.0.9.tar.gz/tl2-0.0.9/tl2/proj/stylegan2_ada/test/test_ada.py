import os
import sys
import unittest

import torch

from tl2.proj.stylegan2_ada import persistence


# @MODEL_REGISTRY.register(name_prefix=__name__)
@persistence.persistent_class
class PersistenceNetwork(torch.nn.Module):
  def __init__(self, num_inputs, num_outputs):
    super().__init__()
    self.fc = torch.nn.Linear(num_inputs, num_outputs)
    pass
  def forward(self, x):
    out = self.fc(x)
    return out


class Testing_persistence(unittest.TestCase):

  def test_persistence_usage(self, debug=True):
    """
    Usage:
        python template_lib/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/pypi/torch1_7_0 -d /cache/pypi -t copytree
        for filename in /cache/pypi/*.whl; do
            pip install $filename
        done
        proj_root=moco-exp
        python template_lib/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        pip install -r requirements.txt

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

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    PORT = os.environ.get('PORT', 8888)

    from tl2.proj.stylegan2_ada import ada_utils

    net = PersistenceNetwork(3, 6)

    snapshot_pkl = f"{args.tl_outdir}/net.pkl"
    ada_utils.save_model(net, snapshot_pkl=snapshot_pkl)

    pass

  def test_load_persistence_model(self, debug=True):
    """
    Usage:
        python template_lib/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/pypi/torch1_7_0 -d /cache/pypi -t copytree
        for filename in /cache/pypi/*.whl; do
            pip install $filename
        done
        proj_root=moco-exp
        python template_lib/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        pip install -r requirements.txt

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

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    PORT = os.environ.get('PORT', 8888)

    import pickle
    from tl2.proj.stylegan2_ada import ada_utils
    from tl2.proj.pytorch.pytorch_hook import VerboseModel

    snapshot_pkl = f"results/persistence/persistence_usage/net.pkl"

    net = ada_utils.load_model(snapshot_pkl)

    net_verbose = VerboseModel(net).cuda()
    x = torch.rand((2, 3)).cuda()
    out = net_verbose(x)
    pass










