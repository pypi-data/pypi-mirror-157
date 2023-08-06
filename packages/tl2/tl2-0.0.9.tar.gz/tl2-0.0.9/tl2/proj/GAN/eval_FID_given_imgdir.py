import argparse

from tl2 import tl2_utils
from tl2.proj.logger import logging_utils_v2

from torch_fidelity.datasets import ImagesPathDataset
from torch_fidelity import calculate_metrics

def main(outdir,
         fake_dir,
         dataset_root,
         debug,
         ):

  logger = logging_utils_v2.get_logger(filename=f"{outdir}/log.txt")

  fake_image_list = tl2_utils.get_filelist_recursive(fake_dir)
  image_list = tl2_utils.get_filelist_recursive(dataset_root)

  if debug:
    fake_image_list = fake_image_list[:10]
    image_list = image_list[:10]

  fake_dataset = ImagesPathDataset(files=fake_image_list)
  real_dataset = ImagesPathDataset(files=image_list)
  logger.info(f"Number of fake images: {len(fake_image_list)}, {fake_dataset[0].shape}")
  logger.info(f"Number of real images: {len(image_list)}, {real_dataset[0].shape}")

  assert fake_dataset[0].shape == real_dataset[0].shape
  metrics_dict = calculate_metrics(input1=fake_dataset,
                                   input2=real_dataset,
                                   cuda=True,
                                   isc=True,
                                   fid=True,
                                   kid=True if not debug else False,
                                   verbose=False)
  logger.info(tl2_utils.dict2string(metrics_dict))

  pass


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--outdir", default="")
  parser.add_argument("--fake_dir", default="")
  parser.add_argument("--dataset_root", default="")
  parser.add_argument("--debug", action="store_true")
  args, _ = parser.parse_known_args()

  print(f"args: \n{tl2_utils.dict2string(vars(args))}")

  main(outdir=args.outdir,
       fake_dir=args.fake_dir,
       dataset_root=args.dataset_root,
       debug=args.debug)
