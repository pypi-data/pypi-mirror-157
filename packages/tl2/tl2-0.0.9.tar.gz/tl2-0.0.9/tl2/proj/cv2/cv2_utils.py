import shutil
import imageio
from pathlib import Path
import os
import sys
import unittest
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import matplotlib.pyplot as plt
import copy
import uuid
from termcolor import cprint


def create_video_from_image_list(video_file_or_path,
                                 image_list,
                                 fps,
                                 del_source_file=False):
  if os.path.isdir(video_file_or_path):
    video_file = f"{video_file_or_path}/{Path(image_list[0]).stem}.mp4"
  else:
    video_file = video_file_or_path

  cprint(f"Create video {video_file}", color='red')

  temp_file = f"{video_file}-{uuid.uuid4().hex}.mp4"
  writer = imageio.get_writer(temp_file, fps=fps)

  for file in image_list:
    im = imageio.imread(file)
    writer.append_data(im)
    if del_source_file:
      os.remove(file)
  writer.close()

  os.replace(temp_file, video_file) # atomic
  pass


def get_mask_from_points(img, points, ):
  """
  points: (num_points, 2)
  """
  mask = np.zeros((img.shape[0], img.shape[1]))
  mask = cv2.fillConvexPoly(mask, np.array(points), 1)
  mask = mask.astype(np.bool)
  img_mask = np.zeros_like(img)
  img_mask[mask] = img[mask]
  return mask, img_mask


def cv2_line(img, pt1, pt2, color=(255, 255, 0), thickness=5):
  pt1 = tuple(pt1)
  pt2 = tuple(pt2)
  img = cv2.line(img, pt1=pt1, pt2=pt2, color=color, thickness=thickness)
  return img

def cv2_line_all_points(img, points):
  for i in range(len(points)):
    cv2_line(img, pt1=points[i], pt2=points[(i+1) % len(points)], )
  return img

def cv2_rectangle(img, x, y, w, h, color=(0, 255, 0), thickness=5):
  img = img.copy()
  cv2.rectangle(img, (x, y), (x + w, y + h), color=color, thickness=thickness)
  return img


def cv2_landmarks(img, landmarks, radius=5, color=(255, 0, 0), thickness=-1,
                  add_id=True, fontScale=0.7):
  img = img.copy()
  for id, (x, y) in enumerate(landmarks):
    if add_id:
      cv2_putText(img, text=str(id), org=(x, y), fontScale=fontScale)
    cv2.circle(img, (x, y), radius=radius, color=color, thickness=thickness)
  return img

def cv2_putText(img,
                text,
                org, # (x, y),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.75,
                color=(0, 255, 0),
                thickness=2):
  cv2.putText(img, text=text, org=org, fontFace=fontFace, fontScale=fontScale, color=color, thickness=thickness)
  return img

def imshow_pil(img_np, is_bgr=False):
  import matplotlib.pyplot as plt
  img_pil = cv2_to_pil(img_np, is_bgr=is_bgr)
  plt.imshow(img_pil)
  plt.show()


def cv2_imread(filename):
  filename = str(filename)
  img_cv = cv2.imread(filename=filename)
  return img_cv


def pad_mirror(width, height, img_np):

  h, w, c = img_np.shape
  start_h = (height - h) // 2
  end_h = start_h + h
  start_w = (width - w) // 2
  end_w = start_w + w

  border_t = start_h
  border_b = height - end_h
  border_l = start_w
  border_r = width - end_w

  # canvas = np.zeros([height, width, 3], dtype=np.uint8)
  # canvas[start_h:end_h, start_w:end_w, :] = img
  canvas = cv2.copyMakeBorder(img_np.copy(), border_t, border_b, border_l, border_r, cv2.BORDER_REFLECT_101)
  return canvas


def get_frame_count(video_file="",
                    cap=None):
  if cap is None:
    cap = cv2.VideoCapture(video_file)
  length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  return length

def open_video(video_file):
  cap = cv2.VideoCapture(str(video_file))
  ret_success, frame = cap.read()
  return ret_success, frame


def cv2_to_pil(img, is_bgr=False, range01=False, ):
  if range01:
    img = (img * 255)
  if img.dtype != np.uint8:
    img = img.astype(np.uint8)

  if is_bgr:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  im_pil = Image.fromarray(img)
  return im_pil


class VideoWriter(object):
  def __init__(self, outfile, w, h, fps):
    self.w = w
    self.h = h
    out_size = (w, h)
    self.video = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*'mp4v'), fps, out_size)
    pass

  def write(self, image, is_tensor=True, rgb=True):
    if is_tensor:
      from torchvision.transforms.functional import to_pil_image
      image = to_pil_image(image)
    image = np.array(image)
    if rgb:
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    assert image.shape[:2] == (self.h, self.w)
    self.video.write(image)
    pass

  def release(self):
    self.video.release()
    pass


class ImageioVideoWriter(object):
  def __init__(self,
               outfile,
               fps,
               save_gif=False,
               hd_video=True,
               gif_interval=1,
               **kwargs):
    """
    pip install imageio-ffmpeg opencv-python

    :param outfile:
    :param fps:
    :param save_gif:
    :param hd_video:
    :param quality:
      Video output quality. Default is 5. Uses variable bit rate. Highest quality is 10, lowest is 0.
    [https://imageio.readthedocs.io/en/stable/format_ffmpeg.html?highlight=codec#parameters-for-saving](https://imageio.readthedocs.io/en/stable/format_ffmpeg.html?highlight=codec#parameters-for-saving)

    :param kwargs:
    """

    self.video_file = outfile
    outfile = Path(outfile)
    self.gif_file = f"{outfile.parent}/{outfile.stem}.gif"
    self.save_gif = save_gif
    self.gif_interval = gif_interval

    self.counter = 0

    self.video = imageio.get_writer(outfile, fps=fps)
    if hd_video:
      outfile_hd = f"{outfile.parent}/{outfile.stem}_hd.mp4"
      self.video_file_hd = outfile_hd
      self.video_hd = imageio.get_writer(outfile_hd, mode='I', fps=fps, codec='libx264', bitrate='16M')
    else:
      self.video_hd = None

    if self.save_gif:
      self.gif_out = imageio.get_writer(self.gif_file, fps=fps//gif_interval)

    pass

  def write(self, image, dst_size=None, **kwargs):
    if dst_size is not None:
      w, h = self._get_size(w=image.size[0], h=image.size[1], dst_size=dst_size, for_min_edge=False)
      if image.size != (w, h):
        image = image.resize((w, h), Image.LANCZOS)
    img_np = np.array(image)
    self.video.append_data(img_np)
    if self.video_hd is not None:
      self.video_hd.append_data(img_np)

    if self.save_gif:
      if self.counter % self.gif_interval == 0:
        self.gif_out.append_data(img_np)

    self.counter += 1
    pass

  def release(self, st_video=False, st_gif=False):
    if self.video_hd is not None:
      print(f"Save to {self.video_file_hd}")
    else:
      print(f"Save to {self.video_file}")
    self.video.close()
    if self.video_hd is not None:
      self.video_hd.close()

    if self.save_gif:
      self.gif_out.close()
      if st_gif:
        import streamlit as st
        st.image(self.gif_file)
        st.write(self.gif_file)
    if st_video:
      import streamlit as st
      if self.video_hd is not None:
        st.video(self.video_file_hd)
        st.write(self.video_file_hd)
      else:
        st.video(self.video_file)
        st.write(self.video_file)
    pass

  def _get_size(self, w, h, dst_size, for_min_edge=True):
    if for_min_edge:
      edge = min(w, h)
    else:
      edge = max(w, h)

    w = int(dst_size / edge * w)
    h = int(dst_size / edge * h)
    return w, h


class Testing_cv2_utils(unittest.TestCase):

  def test_zoom_in_video_writer(self, debug=True):
    """
    Usage:
        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=./exp:./stylegan2-pytorch:./
        python 	-c "from exp.tests.test_styleganv2 import Testing_stylegan2;\
          Testing_stylegan2().test_train_ffhq_128()"

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0' if utils.is_debugging() else '0'
    from template_lib.v2.config_cfgnode.argparser import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    import tqdm
    from template_lib.proj.pil.pil_utils import get_size

    img_path = "template_lib/datasets/images/zebra_GT_target_origin.png"
    outvid = f"{args.tl_outdir}/test.mp4"

    out_size = 2048
    image = Image.open(img_path)
    w, h = image.size
    max_scale = out_size / min(w, h)
    out_w, out_h = get_size(w=w, h=h, dst_size=out_size)

    out_video = VideoWriter(outfile=outvid, w=out_w, h=out_h, fps=10)

    for scale in tqdm.tqdm(np.arange(1, max_scale, 0.05)):
      out_img = Image.new(mode='RGB', size=(out_w, out_h), color='black')
      cur_w, cur_h = int(w * scale), int(h * scale)
      cur_image = image.resize((cur_w, cur_h), resample=Image.NEAREST)
      xy = (out_w - cur_w) // 2, (out_h - cur_h) // 2
      out_img.paste(cur_image, xy)
      out_video.write(out_img, is_tensor=False, rgb=True)
    out_video.release()
    pass


class Testing_Tools(unittest.TestCase):

  def test__extract_frames(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=0
        export PORT=12346
        export PYTHONPATH=.:./piGAN_lib
        python -c "from exp.tests.test_3D_emb import Testing_Evaluation;\
          Testing_Evaluation().test_save_images_nerfgan_no_aug(debug=False)"

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '1'
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

    # debug = False

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file None
                --tl_command None
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                {"--tl_debug" if debug else ""}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    os.environ['PATH'] = f"{os.path.dirname(sys.executable)}:{os.environ['PATH']}"
    os.environ['TORCH_EXTENSIONS_DIR'] = "torch_extensions"

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
    PORT = os.environ.get('PORT', 8888)

    import cv2
    from pathlib import Path
    from tl2.launch.launch_utils import global_cfg
    from tl2.proj.cv2 import cv2_utils
    from tl2.proj.pil import pil_utils

    # video_file = Path("datasets/videos/nerfgan/seed_8624.mp4")
    video_file = Path("datasets/videos/nerfgan/seed_4840.mp4")

    cap = cv2.VideoCapture(str(video_file))

    count = 0
    while True:
      ret_success, frame = cap.read()
      if not ret_success:
        break
      img_pil = cv2_utils.cv2_to_pil(frame, is_bgr=True)
      if debug:
        pil_utils.imshow_pil(img_pil)

      save_path = f"{outdir}/imgdir/{video_file.stem}_{count:03d}.jpg"
      count += 1
      img_pil.save(save_path)

    print(outdir)
    pass





