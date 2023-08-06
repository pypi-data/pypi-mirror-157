import time
import numpy as np
import logging, os
import datetime
import sys
from termcolor import colored
import unittest
import copy

FORMAT = "[%(levelname)s]: %(message)s [%(name)s][%(filename)s:%(funcName)s():%(lineno)s][%(asctime)s.%(msecs)03d]"
DATEFMT = '%Y/%m/%d %H:%M:%S'


class _ColorfulFormatter(logging.Formatter):
  def __init__(self, *args, **kwargs):
    self._root_name = kwargs.pop("root_name") + "."
    self._abbrev_name = kwargs.pop("abbrev_name", "")
    if len(self._abbrev_name):
      self._abbrev_name = self._abbrev_name + "."
    super(_ColorfulFormatter, self).__init__(*args, **kwargs)

  def formatMessage(self, record):
    record.name = record.name.replace(self._root_name, self._abbrev_name)
    log = super(_ColorfulFormatter, self).formatMessage(record)
    if record.levelno == logging.WARNING:
      prefix = colored("WARNING", "red", attrs=["blink"])
    elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
      prefix = colored("ERROR", "red", attrs=["blink", "underline"])
    else:
      return log
    return prefix + " " + log


def logging_init(filename=None, level=logging.INFO, correct_time=False):
  def beijing(sec, what):
    '''sec and what is unused.'''
    beijing_time = datetime.datetime.now() + datetime.timedelta(hours=8)
    return beijing_time.timetuple()

  if correct_time:
    logging.Formatter.converter = beijing

  logging.basicConfig(level=level,
                      format=FORMAT,
                      datefmt=DATEFMT,
                      filename=None, filemode='w')
  logger = logging.getLogger()

  # consoleHandler = logging.StreamHandler()
  # logger.addHandler(consoleHandler)

  if filename:
    logger_handler = logging.FileHandler(filename=filename, mode='w')
    logger_handler.setLevel(level=level)
    logger_handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATEFMT))
    logger.addHandler(logger_handler)

  def info_msg(*argv):
    # remove formats
    org_formatters = []
    for handler in logger.handlers:
      org_formatters.append(handler.formatter)
      handler.setFormatter(logging.Formatter("%(message)s"))

    logger.info(*argv)

    # restore formats
    for handler, formatter in zip(logger.handlers, org_formatters):
      handler.setFormatter(formatter)

  logger.info_msg = info_msg
  return logger

  # logging.error('There are something wrong', exc_info=True)


def get_root_logger(filename, stream=True, level=logging.INFO):
  logger = logging.getLogger()
  logger.setLevel(level)
  set_hander(logger=logger, filename=filename, stream=stream, level=level)
  return logger


def get_logger(filename,
               logger_names=['template_lib', 'tl'],
               stream=True,
               level=logging.DEBUG,
               mode='a'):
  """

  :param filename:
  :param propagate: whether log to stdout
  :return:
  """
  logger_names = copy.deepcopy(logger_names)
  logger_names += [filename, ]
  for name in logger_names:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    set_hander(logger=logger, filename=filename, stream=stream, level=level, mode=mode)
  return logger


def close_logger_file(logger):
  handlers = list(logger.handlers)
  for handler in handlers:
    logger.removeHandler(handler)
  handler.flush()
  handler.close()
  pass

def get_file_logger(filename,
                    mode='w',
                    logger_names=[],
                    stream=False):
  logger = get_logger(filename=filename, logger_names=logger_names, stream=stream, mode=mode)
  return logger


def set_hander(logger, filename, stream=True, level=logging.INFO, mode='a'):
  formatter = logging.Formatter(
    "[%(asctime)s] %(name)s:%(lineno)s %(levelname)s: %(message)s \t[%(filename)s:%(funcName)s():%(lineno)s]",
    datefmt="%m/%d %H:%M:%S"
  )
  # formatter = logging.Formatter(FORMAT, datefmt=DATEFMT)

  file_hander = logging.FileHandler(filename=filename, mode=mode)
  file_hander.setLevel(level=level)
  file_hander.setFormatter(formatter)
  logger.addHandler(file_hander)

  def info_msg(*argv):
    # remove formats
    org_formatters = []
    for handler in logger.handlers:
      org_formatters.append(handler.formatter)
      handler.setFormatter(logging.Formatter("%(message)s"))

    logger.info(*argv)

    # restore formats
    for handler, formatter in zip(logger.handlers, org_formatters):
      handler.setFormatter(formatter)

  logger.info_msg = info_msg

  if stream:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)

    formatter = _ColorfulFormatter(
      # colored("[%(asctime)s %(name)s]: ", "green") + "%(message)s",
      colored("[%(asctime)s] %(name)s %(levelname)s:", "blue") + \
      "%(message)s \t" + \
      colored("[%(filename)s:%(funcName)s():%(lineno)s]", "blue"),
      datefmt="%m/%d %H:%M:%S",
      root_name='template_lib',
      abbrev_name='tl',
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

  return logger


class StreamToLogger(object):
  """
  Fake file-like stream object that redirects writes to a logger instance.
  """

  def __init__(self, logger):
    self.logger = logger
    self.linebuf = ''

  def write(self, buf):
    buf = buf.rstrip('\n')
    if not buf:
      return
    buf = '<> ' + buf
    # for line in buf.rstrip().splitlines():
    #   self.logger.info_msg(line.rstrip())
    org_formatters = []
    for handler in self.logger.handlers:
      org_formatters.append(handler.formatter)
      handler.setFormatter(logging.Formatter("%(message)s"))
    self.logger.info(buf)
    # restore formats
    for handler, formatter in zip(self.logger.handlers, org_formatters):
      handler.setFormatter(formatter)

  def flush(self):
    pass

  def getvalue(self):
    pass

  def close(self):
    pass


def redirect_print_to_logger(logger, ):
  sl = StreamToLogger(logger)
  sys.stdout = sl
  sys.stderr = sl
  pass


def info_msg(logger, *argv):
  # remove formats
  org_formatters = []
  for handler in logger.handlers:
    org_formatters.append(handler.formatter)
    handler.setFormatter(logging.Formatter("%(message)s"))

  logger.info(*argv)

  # restore formats
  for handler, formatter in zip(logger.handlers, org_formatters):
    handler.setFormatter(formatter)


class Testing_Logger(unittest.TestCase):

  def test_get_file_logger(self, debug=True):
    """
    Usage:

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

    logger = logging.getLogger('tl')

    file1 = f"{args.tl_outdir}/test1.txt"
    file1_f = get_file_logger(file1, stream=True)
    file2 = f"{args.tl_outdir}/test2.txt"
    file2_f = get_file_logger(file2, stream=False)

    for i in range(5):
      logger.info_msg(f"logger {i}")

    for i in range(10):
      file1_f.info_msg(i)
    for i in range(10, 20):
      file2_f.info_msg(i)

    pass



