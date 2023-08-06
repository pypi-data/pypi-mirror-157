import numpy as np


def np_choice(a, size, replace=False):
  return np.random.choice(a, size=size, replace=replace)


def np_deg2rad(degree):
  rad = np.deg2rad(degree)
  return rad


def pd_read_csv(filepath,
                sep=",",
                header="infer"):
  """
              0         1     2   3
    0   bbbbffdd    434343   228  D
    1   bbbWWWff  43545343   289   E
    2  ajkfbdafa   2345345  2312   F

    print X[0]
    0     bbbbffdd
    1     bbbWWWff
    2    ajkfbdafa

  :param filepath:
  :param sep:
  :param header:
  :return:
  """
  import pandas as pd

  data = pd.read_csv(filepath, sep=sep, header=header)
  return data


def np_savez(saved_file, *args, **kwargs):
  np.savez(saved_file, *args, **kwargs)
  pass

def np_load_dict(loaded_file, key):
  loaded_data = np.load(loaded_file, allow_pickle=True)
  data_dict = loaded_data[key][()]
  return data_dict


def get_random_state(seed):
  # np.random.RandomState(seed).randn(w_avg_samples, G.z_dim)
  rand_state = np.random.RandomState(seed)
  return rand_state



