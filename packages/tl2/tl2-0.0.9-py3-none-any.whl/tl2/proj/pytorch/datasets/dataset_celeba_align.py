from pathlib import Path
import PIL

import torch
from torch.utils.data import DataLoader, Dataset
import torch.distributed as dist
from torchvision.utils import make_grid
import torchvision.transforms as transforms
import torchvision.transforms.functional as trans_f

from tl2.tl2_utils import read_image_list_from_files


class CelebA_Align(Dataset):
  """
  python3 -m tl2.tools.get_data_list     \
    --source_dir datasets/celeba/img_align_celeba  \
    --outfile datasets/img_align_celeba.txt  \
    --ext *.jpg
  """

  def __init__(self,
               img_size,
               image_list_file="datasets/img_align_celeba.txt",
               verbose=False,
               **kwargs):
    super().__init__()

    self.verbose = verbose
    self.image_list = read_image_list_from_files(image_list_file)

    assert len(self.image_list) > 0, "Can't find data; make sure you specify the path to your dataset"
    self.transform = transforms.Compose(
      [transforms.Resize(320),
       transforms.CenterCrop(256),
       transforms.ToTensor(),
       transforms.Normalize([0.5], [0.5]),
       transforms.RandomHorizontalFlip(p=0.5),
       transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.NEAREST)])
    pass

  def __len__(self):
    return len(self.image_list)

  def __getitem__(self, index):
    image_path = self.image_list[index][0]
    X = PIL.Image.open(image_path)
    X = self.transform(X)

    if self.verbose:
      return X, image_path
    else:
      return X


def get_dataset_distributed(
      batch_size,
      img_size,
      world_size,
      rank,
      num_workers=4,
      shuffle=True,
      drop_last=False,
      pin_memory=False,
      **kwargs):

  dataset = CelebA_Align(img_size=img_size, verbose=True)

  sampler = torch.utils.data.distributed.DistributedSampler(
    dataset, num_replicas=world_size, rank=rank, shuffle=shuffle)
  dataloader = torch.utils.data.DataLoader(
    dataset,
    sampler=sampler,
    batch_size=batch_size,
    shuffle=False,
    num_workers=num_workers,
    drop_last=drop_last,
    pin_memory=pin_memory,
  )

  return dataloader


def main(rank, world_size):
  from tl2.proj.fvcore import global_cfg
  from tl2.proj.pytorch.ddp import d2_comm, ddp_utils
  from tl2.proj.pil import pil_utils

  batch_size = 3
  data_loader = get_dataset_distributed(
    batch_size=batch_size, img_size=256, world_size=world_size, rank=rank,
    num_workers=0, shuffle=False, )

  data_iter = iter(data_loader)

  data, label = next(data_iter)
  data = data.cuda()

  data_list = ddp_utils.all_gather_to_same_device(data)
  data_list1 = ddp_utils.gather_to_same_device(data)
  label_list = d2_comm.all_gather(label)
  label_name = ""
  for labels in label_list:
    for label in labels:
      label = Path(label)
      label_name += f"{label.stem}_"
    label_name += "\n"

  if data_list1:
    data = torch.cat(data_list1, dim=0)
    merged_data = make_grid(data, nrow=batch_size, normalize=True, scale_each=True)
    img_pil = trans_f.to_pil_image(merged_data)
    caption = f"{data.shape}\n{label_name}"
    caption = caption.strip('\n')
    pil_utils.imshow_pil(img_pil, title=caption)

  d2_comm.synchronize()
  pass


if __name__ == '__main__':
  from tl2.proj.pytorch.ddp import ddp_utils
  from tl2.launch.launch_utils import update_parser_defaults_from_yaml

  rank = ddp_utils.parser_local_rank()
  parser = update_parser_defaults_from_yaml(parser=None, is_main_process=(rank == 0))

  rank, world_size = ddp_utils.ddp_init()

  main(rank, world_size)

