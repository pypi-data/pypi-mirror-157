import pathlib
import collections
from pathlib import Path
import logging
import os
import sys
from PIL import Image
import streamlit as st

sys.path.insert(0, os.getcwd())

from tl2.launch.launch_utils import update_parser_defaults_from_yaml, global_cfg
from tl2.proj.streamlit import SessionState
from tl2.proj.streamlit import st_utils
from tl2.proj.logger.logger_utils import get_file_logger
from tl2 import tl2_utils
from tl2.proj.streamlit import st_utils
from tl2.proj.fvcore import build_model, MODEL_REGISTRY
from tl2.proj.cv2 import cv2_utils
from tl2.proj.pil import pil_utils

# sys.path.insert(0, f"{os.getcwd()}/DGP_lib")
# from DGP_lib import utils
# sys.path.pop(0)


def build_sidebar():
  st.sidebar.text(global_cfg.sidebar.sidebar_name)
  st.sidebar.text(f"{global_cfg.tl_outdir}")
  pass


# @MODEL_REGISTRY.register(name_prefix=__name__)
class STModel(object):
  def __init__(self):

    pass

  def show_video(self,
                 cfg,
                 outdir,
                 saved_suffix_state=None,
                 **kwargs):
    from tl2.proj.streamlit import st_utils

    num_video = st_utils.number_input('num_video', cfg.num_video, sidebar=True)
    for idx in range(num_video):
      tag = st_utils.text_input(f"tag {idx}", "", sidebar=True)
      video_path = st_utils.text_input(f"video {idx} ", "", sidebar=True)
      if video_path and os.path.isfile(video_path):
        st.subheader(f"tag {idx}: {tag}")
        if video_path.endswith(('.jpg', '.png')):
          st.image(video_path)
        elif video_path.endswith('.mp4'):
          st.video(video_path)
        st.write(video_path)

    if not global_cfg.tl_debug:
      if not st.sidebar.button("run_web"):
        return

    if saved_suffix_state is not None:
      saved_suffix_state.saved_suffix = saved_suffix_state.saved_suffix + 1

    pass

  def show_results(self,
                   cfg,
                   outdir,
                   saved_suffix_state=None,
                   **kwargs):

    results_dir = st_utils.text_input('results_dir', cfg.results_dir, sidebar=False)
    show_png = st_utils.checkbox('show_png', True, sidebar=True)
    show_jpg = st_utils.checkbox('show_jpg', False, sidebar=True)

    if results_dir and os.path.isdir(results_dir):
      video_files = tl2_utils.get_filelist_recursive(results_dir, ext="*.mp4", sort=False)
      for video_file in video_files:
        video_file = str(video_file)
        st.video(video_file)
        st.write(video_file)

      if show_png:
        png_files = tl2_utils.get_filelist_recursive(results_dir, ext="*.png", sort=False)
        for png_file in png_files:
          png_file = str(png_file)
          st.image(png_file)
          st.write(png_file)

      if show_jpg:
        jpg_files = tl2_utils.get_filelist_recursive(results_dir, ext="*.jpg", sort=False)
        for jpg_file in jpg_files:
          jpg_file = str(jpg_file)
          st.image(jpg_file)
          st.write(jpg_file)

    if not global_cfg.tl_debug:
      if not st.sidebar.button("run_web"):
        return

    if saved_suffix_state is not None:
      saved_suffix_state.saved_suffix = saved_suffix_state.saved_suffix + 1

    pass

  def show_image_list(self,
                      cfg,
                      outdir,
                      saved_suffix_state=None,
                      **kwargs):
    import collections
    from tl2.proj.streamlit import st_utils
    from tl2.proj.pil import pil_utils

    image_list_kwargs = collections.defaultdict(dict)
    for k, v in cfg.image_list_files.items():
      header = f"{k}_s"
      image_path = st_utils.parse_image_list(image_list_file=v.image_list_file, header=header, )
      image_list_kwargs[header]['image_path'] = image_path
      header = f"{k}_t"
      image_path = st_utils.parse_image_list(image_list_file=v.image_list_file, header=header, )
      image_list_kwargs[header]['image_path'] = image_path
    source_k = st_utils.radio('source', options=image_list_kwargs.keys(), index=0, sidebar=True)
    target_k = st_utils.radio('target', options=image_list_kwargs.keys(), index=1, sidebar=True)

    image_path_s = image_list_kwargs[source_k]['image_path']
    image_path_t = image_list_kwargs[target_k]['image_path']

    img_pil_s = Image.open(image_path_s)
    img_pil_t = Image.open(image_path_t)
    img_pil_s_t = pil_utils.merge_image_pil([img_pil_s, img_pil_t], nrow=2, pad=1, dst_size=2048)
    st.image(img_pil_s_t, caption=f"source: {img_pil_s.size}, target: {img_pil_t.size}", use_column_width=True)

    # ****************************************************************************
    if not global_cfg.tl_debug:
      if not st.sidebar.button("run_web"):
        return

    if saved_suffix_state is not None:
      saved_suffix_state.saved_suffix = saved_suffix_state.saved_suffix + 1

    pass

  def project_image_web(self,
                        cfg,
                        outdir,
                        saved_suffix_state=None,
                        **kwargs):

    image_list_kwargs = collections.defaultdict(dict)
    for k, v in cfg.image_list_files.items():
      data_k = k
      image_path = st_utils.parse_image_list(image_list_file=v.image_list_file, header=data_k, show_image=False)
      image_list_kwargs[data_k]['image_path'] = image_path

    data_k = st_utils.radio('source', options=image_list_kwargs.keys(), index=0, sidebar=True)
    image_path = image_list_kwargs[data_k]['image_path']
    image_input = st_utils.text_input('input image path:', '')
    if image_input:
      image_path = pathlib.Path(image_input)

    st_utils.st_show_image(image_path)

    img_pil = Image.open(image_path)
    st_utils.st_image(img_pil, caption=f"{img_pil.size}, {data_k}", debug=global_cfg.tl_debug, )
    st.write(image_path)

    # ****************************************************************************
    if not global_cfg.tl_debug:
      if not st.sidebar.button("run_web"):
        return

    if saved_suffix_state is not None:
      saved_suffix_state.saved_suffix = saved_suffix_state.saved_suffix + 1

    # ****************************************************************************

    pass


# @st.cache(allow_output_mutation=True, suppress_st_warning=True)
def build_model_st():
  try:
    model = build_model(global_cfg.model_cfg, cfg_to_kwargs=True)
  except:
    import traceback
    traceback.print_exc()
    model = STModel()
  return model


def main():
  # sys.path.insert(0, f"{os.getcwd()}/BigGAN_Pytorch_lib")

  update_parser_defaults_from_yaml(parser=None)

  # sidebar
  build_sidebar()

  # outdir
  kwargs = {}
  if not global_cfg.tl_debug and global_cfg.get("st_web", True):
    # saved_suffix_state = SessionState.get(saved_suffix=0)
    saved_suffix_state = st.session_state
    if 'saved_suffix' not in saved_suffix_state:
      saved_suffix_state['saved_suffix'] = 0
    saved_suffix = saved_suffix_state.saved_suffix
    kwargs.update({'saved_suffix_state': saved_suffix_state})
  else:
    saved_suffix = 0
  st_saved_suffix = st.empty()
  # st.sidebar.header(f"Outdir: ")
  saved_suffix = st_saved_suffix.number_input(label="Saved dir suffix: ", min_value=0, value=saved_suffix)
  saved_suffix = int(saved_suffix)

  outdir = f"{global_cfg.tl_outdir}/exp/{saved_suffix:04d}"
  kwargs['outdir'] = outdir
  st_utils.st_set_sep(msg='outdir', sidebar=True)
  st.sidebar.write(outdir)
  os.makedirs(outdir, exist_ok=True)

  get_file_logger(filename=f"{outdir}/log.txt", logger_names=['st'])
  logger = logging.getLogger('st')
  # logger.info(f"global_cfg: \n{tl2_utils.dict2string(global_cfg, use_pprint=False)}")
  logger.info(f"global_cfg:\n {global_cfg.dump()}")


  st_model = build_model_st()

  if 'default_mode' in global_cfg:
    mode = st_utils.selectbox(label='mode', options=global_cfg.mode, default_value=global_cfg.default_mode,
                              sidebar=True)
  else:
    mode = st_utils.selectbox(label='mode', options=global_cfg.mode, sidebar=True)
  
  getattr(st_model, mode)(cfg=global_cfg.get(mode, {}), **kwargs)

  pass

if __name__ == '__main__':
  main()
