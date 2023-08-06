import io
import copy
import numpy as np
import time
import glob
from pathlib import Path
import tqdm
import argparse
import os
import re
import logging
import sys
import importlib
import json
import pprint
import collections
from operator import attrgetter
import zipfile
import shutil
from datetime import datetime, timedelta
import multiprocessing
import hashlib
import tempfile
import pickle


def int2bitstring(number):
  """
  3 -> '11'

  Args:
      number ([type]): [description]

  Returns:
      [type]: [description]
  """
  return f"{number:b}"

def bitstring2int(bit_string):
  """
  '11' -> 3

  3 ^ 3 = 0
  3 & 3 = 3
  3 << 1 = 6

  Args:
      bit_string ([type]): [description]

  Returns:
      [type]: [description]
  """
  bit_int = int(bit_string, 2)
  return bit_int


def pickle_dump(saved_path,
                data):

  with open(saved_path, 'wb') as f:
    pickle.dump(data, f)

  # with open(saved_path, 'rb') as f:
  #   data = pickle.load(f)

def load_pickle_file(pkl_path):
  with open(pkl_path, 'rb') as f:
    data = pickle.load(f, encoding='latin1')
  return data

def write_pickle_file(pkl_path,
                      data_dict):
  with open(pkl_path, 'wb') as fp:
    pickle.dump(data_dict, fp, protocol=2)


def get_tempfile():
  """
  temp_file.close()

  """
  temp_file = tempfile.TemporaryFile('w+t')
  return temp_file


def get_tempdir():
  temp_dir = tempfile.TemporaryDirectory()
  return temp_dir


class TL_tqdm(object):
  def __repr__(self):
    return str(self.pbar)

  def __init__(self,
               total,
               start=0,
               desc=''):

    self.pbar_io = get_tempfile()

    self.pbar = tqdm.tqdm(total=total, desc=desc, file=self.pbar_io)

    if start > 0:
      self.pbar.update(start)

    # self.pbar_range = range(start, total)
    self.start = start
    self.total = total
    self._count = start - 1
    pass

  def __iter__(self):
    self._count = self.start - 1
    self.pbar.reset()
    return self

  def __next__(self):
    self._count += 1
    if self._count < self.total:
      self.update(1)
      return self._count
    else:
      raise StopIteration

  def __del__(self):
    self.pbar_io.close()
    pass

  def update(self, n=1):
    self.pbar.update(n)

  def get_string(self):
    return str(self.pbar)


def os_system(command):
  print(f"\n+ {command}\n")
  os.system(command)
  pass


def get_class_repr(self, prefix=''):
  """
  self.repr_str = tl2_utils.dict2string()
  self.module_name_list = []

  :param self:
  :return:
  """
  repr_str = f"{prefix}.{self.__class__.__name__}({self.repr_str})"
  return repr_str

def print_repr(self):
  """
  self.module_name_list = []

  :param self:
  :return:
  """
  from tl2.proj.pytorch import torch_utils

  models_dict = {}
  for name in self.module_name_list:
    models_dict[name] = attrgetter_default(object=self, attr=name)
  models_dict['All'] = self
  logger = logging.getLogger('tl')
  torch_utils.print_number_params(models_dict=models_dict, logger=logger)
  logger.info(self)
  pass

def to_dict_recursive(dict_input):

  ret_dict = collections.OrderedDict()
  for k, v in dict_input.items():
    if isinstance(v, dict):
      ret_dict[k] = to_dict_recursive(v)
    else:
      ret_dict[k] = v
  return ret_dict

def get_diff_str(d1, d2):
  from deepdiff import DeepDiff
  d1 = to_dict_recursive(d1)
  d2 = to_dict_recursive(d2)

  ddiff = DeepDiff(d1, d2)
  diff_str = "**********************************************************\n"
  diff_str += f"Modification of d2 compared to d1: \n{ddiff.pretty()}\n"
  diff_str += "**********************************************************"
  return diff_str


def write_info_msg(saved_dir,
                   info_msg):
  with open(f"{saved_dir}/0info.txt", 'w') as f:
    f.write(f"{info_msg}\n")
  pass


def get_string_md5(string):
  str_md5 = hashlib.md5(string.encode("utf-8")).hexdigest()
  return str_md5

tl_last_print_time = 0
def get_print_dict_str(metric_dict,
                       float_format="+1.6f",
                       outdir='',
                       suffix_str=''):
  ret_str = f"=> {outdir} [GPU: {os.environ.get('CUDA_VISIBLE_DEVICES', '0')}]"

  if not isinstance(metric_dict, collections.defaultdict):
    metric_dict = {'tmp': metric_dict}

  for _, v_dict in metric_dict.items():
    for k, v in v_dict.items():
      if isinstance(v, float):
        ret_str += f" [{k}: {v:{float_format}}]"
      else:
        ret_str += f" [{k}: {v}]"

  now = time.time()
  global tl_last_print_time
  elapsed = now - tl_last_print_time
  tl_last_print_time = now
  ret_str += f" [elapsed: {elapsed:.3f}s]"

  if suffix_str:
    ret_str += f" [{suffix_str}]"
  return ret_str


class AverageMeter():
  """ Computes and stores the average and current value """

  def __init__(self):
    self.reset()

  def reset(self):
    """ Reset all statistics """
    self.val = 0
    self.avg = 0
    self.sum = 0
    self.count = 0

  def update(self,
             val,
             n=1):
    """ Update statistics """
    self.val = val
    self.sum += val * n
    self.count += n
    self.avg = self.sum / self.count
    pass


def get_randomstate(seed):
  """
  random_state.shuffle()

  :param seed:
  :return:
  """
  random_state = np.random.RandomState(seed)
  return random_state


class Worker(multiprocessing.Process):
  """
  command[0].startswith(('bash', )):
  p = Worker(name='Command worker', args=(command[0],))
  p.start()
  """
  def run(self):
    command = self._args[0].strip()
    command = f"export PATH={os.path.dirname(sys.executable)}:$PATH && " + command
    print('%s'%command)
    # start_cmd_run(command)
    os.system(command)
    return


def get_time_str():
  time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
  return time_str


def time2string(elapsed):
  """
  elapsed = time.time() - time_start
  """
  # hours, rem = divmod(elapsed, 3600)
  # minutes, seconds = divmod(rem, 60)
  # time_str = "{:0>2}h:{:0>2}m:{:05.2f}s".format(int(hours), int(minutes), seconds)
  time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
  return time_str

def time_ns2string(time_start):
  """
  python >= 3.7

  1s = 10^9 ns

  time_start = time.perf_counter_ns()
  time_end = time.perf_counter_ns()
  elapsed = time_end - time_start

  """
  time_end = time.perf_counter_ns()
  elapsed = time_end - time_start

  time_str = f"{elapsed} ns"
  return time_str


def time_us2string(time_start, repeat_times=None):
  """
  1s = 10^6 us

  time_start = time.perf_counter()
  time_end = time.perf_counter()
  elapsed = time_end - time_start

  return: s (precise us)
  """
  time_end = time.perf_counter()
  elapsed = time_end - time_start

  time_str = f"all (repeat={repeat_times}): {elapsed} s"

  if repeat_times is None:
    repeat_times = 1.

  time_str += f", all/repeat: {elapsed/repeat_times} s"

  time_str += f", fps: {1. / (elapsed / repeat_times)}"

  return time_str

def get_time_since_last_md(filepath):

  modi_time = datetime.fromtimestamp(os.path.getmtime(filepath))
  modi_inter = datetime.now() - modi_time
  modi_minutes = modi_inter.total_seconds() // 60
  return int(modi_minutes)


_circle_dict = {}
class CircleNumber(object):
  def __init__(self, max_to_keep=4):
    self.max_to_keep = max_to_keep
    self.cur_num = -1
    pass

  @staticmethod
  def get_named_circle(name,
                       max_to_keep=2):

    if name not in _circle_dict:
      named_circle = CircleNumber(max_to_keep=max_to_keep)
      _circle_dict[name] = named_circle
    else:
      named_circle = _circle_dict[name]

    return named_circle

  def get_number(self, ):
    self.cur_num += 1
    self.cur_num = self.cur_num % self.max_to_keep
    number = f"{self.cur_num:02d}"
    return number


_MaxToKeep_dict = {}

class MaxToKeep(object):
  def __init__(self,
               max_to_keep=None,
               use_circle_number=True):
    self.max_to_keep = max_to_keep
    self.recent_checkpoints = []

    if use_circle_number and max_to_keep > 0:
      self.circle_number_gen = CircleNumber(max_to_keep=max_to_keep)
    pass

  @staticmethod
  def get_named_max_to_keep(name,
                            max_to_keep=2,
                            use_circle_number=True):

    if name not in _MaxToKeep_dict:
      named_maxtokeep = MaxToKeep(max_to_keep=max_to_keep, use_circle_number=use_circle_number)
      _MaxToKeep_dict[name] = named_maxtokeep
    else:
      named_maxtokeep = _MaxToKeep_dict[name]

    return named_maxtokeep

  def step(self, file_path):
    if self.max_to_keep is not None:
      self.recent_checkpoints.append(file_path)
      if len(self.recent_checkpoints) > self.max_to_keep:
        file_to_delete = self.recent_checkpoints.pop(0)
        if os.path.exists(file_to_delete):
          if os.path.isdir(file_to_delete):
            shutil.rmtree(file_to_delete)
          else:
            os.remove(file_to_delete)
    pass

  def step_and_ret_circle_dir(self,
                              root_dir,
                              info_msg=None):
    os.makedirs(root_dir, exist_ok=True)
    cur_number = self.circle_number_gen.get_number()
    last_files = glob.glob(f"{root_dir}/0recent_*.txt")
    for last_file in last_files:
      if os.path.isfile(last_file):
        os.remove(last_file)
    with open(f"{root_dir}/0recent_{cur_number}.txt", 'w') as f:
      f.write(f"{info_msg}\n")

    dst_dir = os.path.join(root_dir, str(cur_number))

    self.step(dst_dir)

    os.makedirs(dst_dir, exist_ok=True)
    if info_msg is not None:
      with open(f"{dst_dir}/0info.txt", 'w') as f:
        f.write(f"{info_msg}\n")

    return dst_dir


def make_zip(source_dir, output_filename):
  import zipfile
  zipf = zipfile.ZipFile(output_filename, 'w')
  pre_len = len(os.path.dirname(source_dir))
  for parent, dirnames, filenames in os.walk(source_dir):
    for filename in filenames:
      pathfile = os.path.join(parent, filename)
      arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
      zipf.write(pathfile, arcname)
  zipf.close()


def unzip_file(zip_file, dst_dir):
  os.makedirs(dst_dir, exist_ok=True)
  assert zipfile.is_zipfile(zip_file)

  fz = zipfile.ZipFile(zip_file, 'r')
  for file in fz.namelist():
    fz.extract(file, dst_dir)
  fz.close()
  print(f'Unzip {zip_file} to {dst_dir}')


def get_filelist_recursive(directory,
                           ext=('*.jpg', '*.png'),
                           sort=True,
                           to_str=False,
                           recursive=True):

  if not isinstance(ext, (list, tuple)):
    ext = [ext]
  file_list = []
  for _ext in ext:
    if recursive:
      file_list.extend(list(Path(directory).rglob(_ext)))
    else:
      file_list.extend(list(Path(directory).glob(_ext)))
  if sort:
    file_list = sorted(file_list, key=lambda path: path.name)

  if to_str:
    func = lambda x: str(x)
    file_list = list(map(func, file_list))

  return file_list


def check_image_list_validity(image_file):
  image_list = read_image_list_from_files(image_file)
  pbar = tqdm.tqdm(image_list)
  for idx, image_path in enumerate(pbar, start=1):
    if isinstance(image_path, list):
      image_path = image_path[0]
    if not os.path.exists(image_path):
      print(f"Error: {idx}: {image_path}")
  pass


def read_image_list_from_files(image_list_file,
                               compress=False,
                               ext=('*.jpg', '*.png', '*.jpeg')):
  """

  :param image_list_file: [image_list.txt, ] or [image_dir, ]
  :param compress:
  :param ext:
  :return:
  """
  if not isinstance(image_list_file, (list, tuple)):
    image_list_file = [image_list_file, ]

  all_image_list = []
  for image_file in image_list_file:
    if os.path.isdir(image_file):
      image_list = get_filelist_recursive(image_file, ext=ext)
      image_list = list(map(lambda x: [str(x)], image_list))
    else:
      with open(image_file) as f:
        image_list = f.readlines()
      image_list = [v.strip().split(' ') for v in image_list]
    all_image_list.extend(image_list)

  if compress:
    all_image_list = list(map(lambda x: x[0] if len(x) == 1 else x, all_image_list))
  return all_image_list


def attrgetter_default(object, attr, default=None):
  ret = default
  try:
    ret = attrgetter(attr)(object)
  except:
    pass
  return ret

class TermColor(object):
  """
  export ANSI_COLORS_DISABLED=1
  """
  def __init__(self):
    from termcolor import colored, COLORS
    self.black = 'grey'
    self.green = 'green'
    self.colors = ['red', 'yellow', 'blue', 'magenta', 'cyan']
    self.cur_color = 0
    pass

  def get_a_color(self):
    color = self.colors[self.cur_color]
    self.cur_color += 1
    return color


def dict2string(dict_obj, use_pprint=True, prefix_str=''):
  dict_obj = copy.deepcopy(dict_obj)
  dict_obj = to_dict_recursive(dict_obj)
  message = ''
  message += f'{prefix_str} ----------------- start ---------------\n'
  if use_pprint:
    message += pprint.pformat(collections.OrderedDict(dict_obj))
  else:
    message += json.dumps(dict_obj, indent=2)
  message += '\n----------------- End -------------------'
  return message


def json_dump(obj_dict, file_path):
  with open(file_path, 'w') as f:
    json.dump(obj_dict, f, indent=2)
  pass


def parser_args_from_list(name, argv_list, type='list'):
  """

  :param name: '--tl_opts'
  :param argv_list:
  :return:
  """
  print(f"Parsering {name} from \n{argv_list}")
  parser = argparse.ArgumentParser()
  if type == 'list':
    parser.add_argument(name, type=str, nargs='*', default=[])
  else:
    parser.add_argument(name)
  args, _ = parser.parse_known_args(args=argv_list)

  value = getattr(args, name.strip('-').replace('-', '_'))
  print(f"{name}={value}")
  return value


def is_debugging():
  import sys
  gettrace = getattr(sys, 'gettrace', None)

  if gettrace is None:
    assert 0, ('No sys.gettrace')
  elif gettrace():
    return True
  else:
    return False


