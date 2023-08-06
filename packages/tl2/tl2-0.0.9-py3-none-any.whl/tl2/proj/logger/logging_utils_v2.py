import logging
import copy
from termcolor import colored


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


def _set_hander(logger,
                filename,
                stream=True,
                level=logging.INFO,
                mode='a'):

  formatter = logging.Formatter(
    fmt="[%(asctime)s] %(name)s:%(lineno)s %(levelname)s: %(message)s \t[%(filename)s:%(funcName)s():%(lineno)s]",
    datefmt="%m/%d %H:%M:%S")
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
      root_name='tl2',
      abbrev_name='tl2',
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

  return logger


def get_logger(filename,
               logger_names=('tl2', ),
               stream=True,
               level=logging.INFO,
               mode='a'):

  logger_names = list(logger_names) + [filename, ]
  for name in logger_names:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    _set_hander(logger=logger, filename=filename, stream=stream, level=level, mode=mode)
  return logger