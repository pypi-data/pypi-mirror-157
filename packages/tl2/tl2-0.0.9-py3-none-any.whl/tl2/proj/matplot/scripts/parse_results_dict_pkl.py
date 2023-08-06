import argparse
import pickle


def main():
  with open(args.pkl, 'rb') as f:
    loaded_dict = pickle.load(f)
  for dict_index, data_dict in loaded_dict.items():
    print(f"dict index: {dict_index}")
    for data_index in data_dict.keys():
      print(f"\t data index: {data_index}")

  pass


if __name__ == '__main__':
  """
  python -m tl2.proj.matplot.scripts.parse_results_dict_pkl \
    --pkl tl2_lib/tl2/proj/matplot/data/OmniGAN_ImageNet128_results.pkl
  
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--pkl', type=str)

  args = parser.parse_args()
  main()


