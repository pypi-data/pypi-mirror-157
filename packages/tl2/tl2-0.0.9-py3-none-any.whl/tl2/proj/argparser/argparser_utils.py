import json
import argparse



def print_args(args):
  args_str = json.dumps(vars(args), indent=2)
  print(f"args: \n{args_str}")
  return args_str


def get_parser():
  parser = argparse.ArgumentParser()
  return parser


def add_argument_list(parser, name, type, nargs, default=(), help=""):
  """

  :param parser:
  :param name:
  :param type: type of elem in the list
  :param nargs: '+' == 1 or more, '*' == 0 or more, '?' == 0 or 1
  :param default:
  :param help:
  :return:
  """

  parser.add_argument(f"--{name}", type=type, nargs=nargs, default=default, help=help)
  pass

def add_argument_list_of_int(parser, name, nargs="*", default=(), help=""):
  add_argument_list(parser=parser, name=name, type=int, nargs=nargs, default=default, help=help)
  pass

def add_argument_list_of_float(parser, name, nargs="*", default=(), help=""):
  add_argument_list(parser=parser, name=name, type=float, nargs=nargs, default=default, help=help)
  pass

def add_argument_list_of_str(parser, name, nargs="*", default=(), help=""):
  add_argument_list(parser=parser, name=name, type=str, nargs=nargs, default=default, help=help)
  pass


def add_argument_str(parser, name, default="", choices=(), help=""):
  if not choices:
    parser.add_argument(f"--{name}", type=str, default=default, help=help)
  else:
    parser.add_argument(f"--{name}", type=str, choices=choices, help=help, required=True)

  pass

def add_argument_int(parser, name, default=None, help=""):
  parser.add_argument(f"--{name}", type=int, default=default, help=help)
  pass

def add_argument_bool(parser, name, default=False, help=""):
  def str2bool(v):
    if isinstance(v, bool):
      return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
      return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
      return False
    else:
      raise argparse.ArgumentTypeError('Boolean value expected.')

  parser.add_argument(f"--{name}", type=str2bool, nargs='?', const=True, default=default, help=help)
  pass




