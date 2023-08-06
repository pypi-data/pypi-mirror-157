import time
import os
import sys
import json
import logging
import pprint
import subprocess
from datetime import datetime
import argparse

import shutil

import yaml
from easydict import EasyDict

from tl2 import tl2_utils
from tl2.proj.fvcore import global_cfg, TLCfgNode, set_global_cfg
from tl2.proj.logger.logger_utils import get_logger
from tl2.proj.logger import set_global_textlogger, TextLogger
from tl2.proj.pytorch.ddp import d2_comm
from tl2.proj.argparser import argparser_utils


def get_command_and_outdir(
      instance,
      func_name=sys._getframe().f_code.co_name,
      file=__file__):
  # func name
  assert func_name.startswith('test_')
  command = func_name[5:]
  class_name = instance.__class__.__name__
  subdir = class_name[7:] if instance.__class__.__name__.startswith('Testing') else class_name
  subdir = subdir.strip('_')
  outdir = f'results/{subdir}/{command}'

  file = os.path.relpath(file, os.path.curdir)
  file = file.replace('/', '.')
  run_str = f"""
*************************************************************
python -c "from {file[:-3]} import {class_name};\\\n  {class_name}().{func_name}()"\n
*************************************************************
             """
  print(run_str.strip(' '))

  tl_outdir = tl2_utils.parser_args_from_list(name="--tl_outdir", argv_list=sys.argv, type='str')
  if tl_outdir is not None:
    outdir = tl_outdir
    os.environ['TIME_STR'] = '0'
  return command, outdir

def use_moxing():
  tl_mox = True
  try:
    import moxing as mox
  except:
    tl_mox = False
  return tl_mox

def _build_parser(parser=None, append_local_rank=False):
  if not parser:
    parser = argparse.ArgumentParser()
  parser.add_argument('--tl_config_file', type=str, default='')
  parser.add_argument('--tl_command', type=str, default='')
  parser.add_argument('--tl_outdir', type=str, default='results/temp')
  parser.add_argument('--tl_opts', type=str, nargs='*', default=[])
  parser.add_argument('--tl_resume', action='store_true', default=False)
  parser.add_argument('--tl_resumedir', type=str, default='results/temp')
  parser.add_argument('--tl_debug', action='store_true', default=False)
  argparser_utils.add_argument_bool(parser, 'tl_mox', default=use_moxing())

  parser.add_argument('--tl_time_str', type=str, default='')
  if append_local_rank:
    parser.add_argument("--local_rank", type=int, default=0)
  return parser


def _setup_outdir(args, resume):
  if resume:
    args.tl_outdir = args.tl_resumedir
    args.tl_config_file_resume = os.path.join(args.tl_outdir, "config_command.yaml")
    args.tl_time_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
  else:
    TIME_STR = bool(int(os.getenv('TIME_STR', 0)))
    args.tl_time_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    args.tl_outdir = args.tl_outdir if not TIME_STR else (args.tl_outdir + '-' + args.tl_time_str)

    shutil.rmtree(args.tl_outdir, ignore_errors=True)
    _make_dirs(tl_outdir=args.tl_outdir)

  # dirs
  args.tl_abs_outdir = os.path.realpath(args.tl_outdir)

  # files
  args.tl_logfile = os.path.join(args.tl_outdir, "log.txt")
  args.tl_saved_config_file = os.path.join(args.tl_outdir, "config.yaml")
  args.tl_saved_config_command_file = os.path.join(args.tl_outdir, "config_command.yaml")
  pass


def _setup_config(config_file, args):
  """
  Load yaml and save command_cfg
  """
  cfg = TLCfgNode(new_allowed=True)
  cfg.merge_from_file(config_file)
  cfg.dump_to_file(args.tl_saved_config_file)

  command_cfg = TLCfgNode.load_yaml_with_command(config_file, command=args.tl_command)
  command_cfg.merge_from_list(args.tl_opts)

  if args.tl_resume:
    from deepdiff import DeepDiff
    logging.getLogger('tl').info("**********************************************************")
    resume_cfg_file = f"{os.path.dirname(args.tl_config_file_resume)}/config_resume.yaml"
    if not os.path.exists(resume_cfg_file):
      temp_cfg = TLCfgNode.load_yaml_file(args.tl_config_file_resume)
      temp_cfg.dump_to_file(resume_cfg_file)
    else:
      temp_cfg = TLCfgNode.load_yaml_file(resume_cfg_file)
    assert len(temp_cfg) == 1
    resume_cfg = list(temp_cfg.values())[0]

    logging.getLogger('tl').info(f"Updating resume_cfg: {args.tl_config_file_resume}")
    resume_cfg_clone = resume_cfg.clone()
    resume_cfg_clone.update(command_cfg)
    command_cfg =resume_cfg_clone

    ddiff = DeepDiff(resume_cfg, command_cfg)
    logging.getLogger('tl').info(f"diff between resume_cfg and cfg: \n{ddiff.pretty()}")
    logging.getLogger('tl').info("**********************************************************")

  command_cfg.dump_to_file_with_command(saved_file=args.tl_saved_config_command_file,
                                        command=args.tl_command)
  # saved_command_cfg = TLCfgNode(new_allowed=True)
  # setattr(saved_command_cfg, args.tl_command, command_cfg)
  # saved_command_cfg.dump_to_file(args.tl_saved_config_command_file)
  return cfg, command_cfg


def setup_outdir_and_yaml(
      argv_str=None,
      return_cfg=False):
  """
  Usage:

  :return:
  """
  argv_str_list = argv_str.split()
  parser = _build_parser()
  args, unparsed_argv = parser.parse_known_args(args=argv_str_list)

  args = EasyDict(vars(args))
  _setup_outdir(args=args, resume=args.tl_resume)

  # get logger
  logger = get_logger(filename=args.tl_logfile, logger_names=['template_lib', 'tl'], stream=True)
  logger.info('\nargs:\n' + tl2_utils.dict2string(args, use_pprint=False))

  if args.tl_resume:
    logger.info(f"Resume from \n{args.tl_resumedir}")

  # git
  # get_git_hash(logger)

  if args.tl_command.lower() == 'none':
    if return_cfg: return args, None
    else: return args

  # Load yaml
  _, command_cfg = _setup_config(config_file=args.tl_config_file, args=args)
  logger.info(f"\nThe cfg: \n{command_cfg.dump()}")
  if return_cfg:
    global_cfg.merge_from_dict(command_cfg)

    for k, v in vars(args).items():
      if k.startswith('tl_'):
        global_cfg.merge_from_dict({k: v})
    command_cfg.merge_from_dict(global_cfg)
    return args, command_cfg
  else:
    return args


def get_append_cmd_str(args):
  cmd_str_append = f"""
            --tl_config_file {args.tl_saved_config_command_file}
            --tl_command {args.tl_command}
            --tl_outdir {args.tl_outdir}
            {'--tl_resume --tl_resumedir ' + args.tl_resumedir if args.tl_resume else ''}
            --tl_time_str {args.tl_time_str}
            """
  return cmd_str_append


def start_cmd_run(cmd_str):
  cmd = cmd_str.split()
  logger = logging.getLogger('tl')
  logger.info('\nrun_str:\n' + ' \\\n  '.join(cmd))
  current_env = os.environ.copy()
  if cmd[0] == 'python':
    cmd[0] = sys.executable
    process = subprocess.Popen(cmd, env=current_env)
  elif cmd[0] == 'bash':
    process = subprocess.Popen(['/bin/bash', '-o', 'xtrace', '-c', ' '.join(cmd[1:])], env=current_env)
  else:
    process = subprocess.Popen(cmd, env=current_env)

  process.wait()
  if process.returncode != 0:
    raise subprocess.CalledProcessError(returncode=process.returncode, cmd=cmd)
  pass


def _setup_logger_global_cfg_global_textlogger(
      args,
      tl_textdir,
      is_main_process=True):
  # log files
  tl_logfile = os.path.join(args.tl_outdir, "log.txt")
  if is_main_process:
    if len(logging.getLogger('tl').handlers) < 2:
      logger = get_logger(filename=tl_logfile)
  else:
    logger = logging.getLogger('tl')
    logger.propagate = False

  # textlogger
  if is_main_process:
    textlogger = TextLogger(log_root=tl_textdir)
    set_global_textlogger(textlogger=textlogger)

  # Load yaml file and update parser defaults
  if not args.tl_command.lower() == 'none':
    assert os.path.exists(args.tl_config_file)
    cfg = TLCfgNode.load_yaml_with_command(args.tl_config_file, args.tl_command)
    cfg.merge_from_list(args.tl_opts)

    cfg.tl_saved_config_file = f"{args.tl_outdir}/config_command.yaml"
    set_global_cfg(cfg)
    # logging.getLogger('tl').info("\nglobal_cfg: \n" + get_dict_str(global_cfg, use_pprint=False))
    logging.getLogger('tl').info("\nglobal_cfg: \n" + global_cfg.dump())
    # time.sleep(0.1)
    d2_comm.synchronize()
    if is_main_process:
      cfg.dump_to_file_with_command(saved_file=global_cfg.tl_saved_config_file, command=args.tl_command)
      # saved_command_cfg = TLCfgNode(new_allowed=True)
      # setattr(saved_command_cfg, args.tl_command, cfg)
      # saved_command_cfg.dump_to_file(global_cfg.tl_saved_config_file)
  else:
    cfg = TLCfgNode()
    cfg.merge_from_list(args.tl_opts, new_allowed=True)

    cfg.tl_saved_config_file = f"{args.tl_outdir}/config_command.yaml"
    set_global_cfg(cfg)
    logging.getLogger('tl').info("\nglobal_cfg: \n" + tl2_utils.dict2string(global_cfg))
    if is_main_process:
      cfg.dump_to_file_with_command(saved_file=global_cfg.tl_saved_config_file, command=args.tl_command)
  return cfg, tl_logfile


def _parser_set_defaults(parser, cfg, **kwargs):
  if cfg:
    for k, v in cfg.items():
      parser.set_defaults(**{k: v})
  for k, v in kwargs.items():
    parser.set_defaults(**{k: v})
  return parser


def _make_dirs(tl_outdir):
  tl_ckptdir = f'{tl_outdir}/ckptdir'
  tl_imgdir = f'{tl_outdir}/imgdir'
  tl_textdir = f'{tl_outdir}/textdir'

  os.makedirs(tl_outdir, exist_ok=True)
  os.makedirs(tl_ckptdir, exist_ok=True)
  os.makedirs(tl_imgdir, exist_ok=True)
  os.makedirs(tl_textdir, exist_ok=True)
  return tl_ckptdir, tl_imgdir, tl_textdir


def update_parser_defaults_from_yaml(parser, name='args', use_cfg_as_args=False,
                                     is_main_process=True, append_local_rank=False):
  parser = _build_parser(parser, append_local_rank=append_local_rank)

  args, _ = parser.parse_known_args()

  tl_ckptdir, tl_imgdir, tl_textdir = _make_dirs(tl_outdir=args.tl_outdir)

  cfg, tl_logfile = _setup_logger_global_cfg_global_textlogger(args, tl_textdir, is_main_process=is_main_process)

  if use_cfg_as_args:
    default_args = cfg
  else:
    default_args = cfg[name] if name in cfg else None

  _parser_set_defaults(parser, cfg=default_args,
                      tl_imgdir=tl_imgdir, tl_ckptdir=tl_ckptdir, tl_textdir=tl_textdir,
                      tl_logfile=tl_logfile)
  logging.getLogger('tl').info('sys.argv: \n python \n' + ' \n'.join(sys.argv))
  args, _ = parser.parse_known_args()
  for k, v in vars(args).items():
    if k.startswith('tl_'):
      global_cfg.merge_from_dict({k: v})

  # if "register_modules" in global_cfg:
  #   for module in global_cfg.register_modules:
  #     importlib.import_module(module)
  #     logging.getLogger('tl').info(f"Register {module}...")

  return parser


