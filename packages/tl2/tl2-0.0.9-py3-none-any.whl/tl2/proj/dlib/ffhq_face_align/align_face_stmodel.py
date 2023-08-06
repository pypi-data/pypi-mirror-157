import numpy as np
import cv2
import dlib
import collections
from pathlib import Path
import logging
import os
import sys
from PIL import Image
import streamlit as st

sys.path.insert(0, os.getcwd())

from tl2.launch.launch_utils import update_parser_defaults_from_yaml, global_cfg
from tl2.proj.streamlit import st_utils
from tl2 import tl2_utils
from tl2.proj.fvcore import build_model, MODEL_REGISTRY
from tl2.proj.cv2 import cv2_utils
from tl2.proj.dlib import dlib_utils
from tl2.proj.pil import pil_utils
from tl2.modelarts import moxing_utils

from . import align_images


@MODEL_REGISTRY.register(name_prefix=__name__)
class AlignFace(object):
  def __init__(self):

    pass

  def align_face(self,
                 cfg,
                 outdir,
                 saved_suffix_state=None,
                 **kwargs):
    st.write(f"landmark_model: {cfg.landmark_model}")
    image_kwargs = collections.defaultdict(dict)
    key_list = []
    for k, v in cfg.image_list.items():
      key1 = f"{k}1"
      image_path = st_utils.parse_image_list(image_list_file=v.image_list_file, header=key1)
      image_kwargs[key1]['image_path'] = image_path
      key_list.extend([key1, ])

    content_k = st_utils.radio(label='raw', options=key_list, sidebar=True)
    content_kwargs = image_kwargs[content_k]
    image_path = content_kwargs['image_path']

    image_path = st_utils.text_input('image_path', image_path)
    if not image_path:
      image_path = content_kwargs['image_path']

    save_in_source_dir = st_utils.checkbox('save_in_source_dir', cfg.save_in_source_dir, sidebar=True)

    img_pil = Image.open(image_path)
    st.image(img_pil, caption=f"{img_pil.size}")

    if not global_cfg.tl_debug:
      if not st.sidebar.button("run_web"):
        return

    if saved_suffix_state is not None:
      saved_suffix_state.saved_suffix = saved_suffix_state.saved_suffix + 1

    # img_ori_pil = Image.open(image_path)
    # st.header(image_path)
    # st.image(img_ori_pil, caption=f"{img_ori_pil.size}")

    moxing_utils.copy_data(rank=0, global_cfg=global_cfg,
                           datapath_obs=f"{cfg.landmark_model}.bz2",
                           datapath=f"{cfg.landmark_model}.bz2")

    saved_image_list = align_images.align_face(
      image_path=image_path,
      landmark_model=cfg.landmark_model,
      outdir=os.path.dirname(image_path) if save_in_source_dir else outdir)
    for image_file in saved_image_list:
      img_pil = Image.open(image_file)
      st.subheader('Aligned face:')
      st.write(f'{image_file}')
      st.image(img_pil, caption=f"{img_pil.size}", use_column_width=True)

    # show alignment
    detector = dlib.get_frontal_face_detector()  
    shape_predictor = dlib.shape_predictor(cfg.landmark_model)
    for image_file in saved_image_list:
      imgs = []

      img = dlib.load_rgb_image(image_file)
      # imgs.append(img)
      # cv2_utils.imshow_pil(img, is_bgr=False)

      dets = detector(img, 1)
      for detection in dets:
        x, y, w, h = dlib_utils.rect_to_bb(rect=detection)
        img_rect = cv2_utils.cv2_rectangle(img, x, y, w, h, thickness=3)
        imgs.append(img_rect)
        # cv2_utils.imshow_pil(img_rect, is_bgr=False)

        face_landmarks = shape_predictor(img, detection)
        face_landmarks = [(item.x, item.y) for item in face_landmarks.parts()]
        img_landmarks = cv2_utils.cv2_landmarks(img_rect, landmarks=face_landmarks, radius=5)
        imgs.append(img_landmarks)
        # cv2_utils.imshow_pil(img_landmarks)
        merged_pil = pil_utils.merge_image_np(imgs, nrow=len(imgs), pad=1, channel_first=False)
        # pil_utils.imshow_pil(merged_pil)

        st.subheader('Landmarks face:')
        st.image(merged_pil, caption=f"{merged_pil.size}")
    pass

  def crop_face_by_landmarks(self,
                             cfg,
                             outdir,
                             saved_suffix_state=None,
                             **kwargs):
    st.write(f"landmark_model: {cfg.landmark_model}")
    image_kwargs = collections.defaultdict(dict)
    key_list = []
    for k, v in cfg.image_list.items():
      key1 = f"{k}1"
      image_path = st_utils.parse_image_list(image_list_file=v.image_list_file, header=key1)
      image_kwargs[key1]['image_path'] = image_path
      key_list.extend([key1, ])

    content_k = st_utils.radio(label='raw', options=key_list, sidebar=True)
    content_kwargs = image_kwargs[content_k]
    image_path = content_kwargs['image_path']

    # ****************************************************************************
    if not global_cfg.tl_debug:
      if not st.sidebar.button("run_web"):
        return

    if saved_suffix_state is not None:
      saved_suffix_state.saved_suffix = saved_suffix_state.saved_suffix + 1


    saved_image_list = align_images.align_face(
      image_path=image_path, landmark_model=cfg.landmark_model, outdir=outdir)
    for image_file in saved_image_list:
      img_pil = Image.open(image_file)
      st.subheader('Aligned face:')
      st.write(f'{image_file}')
      st.image(img_pil, caption=f"{img_pil.size}", use_column_width=True)

    # show alignment
    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(cfg.landmark_model)
    for image_file in saved_image_list:
      imgs = []

      img = dlib.load_rgb_image(image_file)
      # imgs.append(img)
      # cv2_utils.imshow_pil(img, is_bgr=False)

      dets = detector(img, 1)
      for detection in dets:
        x, y, w, h = dlib_utils.rect_to_bb(rect=detection)
        img_rect = cv2_utils.cv2_rectangle(img, x, y, w, h, thickness=3)
        # imgs.append(img_rect)
        # cv2_utils.imshow_pil(img_rect, is_bgr=False)

        face_landmarks = shape_predictor(img, detection)
        face_landmarks = [(item.x, item.y) for item in face_landmarks.parts()]
        img_landmarks = cv2_utils.cv2_landmarks(img_rect, landmarks=face_landmarks, radius=5)
        imgs.append(img_landmarks)
        # cv2_utils.imshow_pil(img_landmarks)

        # crop face
        routes = {}
        landmark_tuple = face_landmarks
        for idx in range(16, -1, -1):
          routes[idx] = landmark_tuple[idx]

        for idx in range(17, 20): # 17, 18, 19
          from_coordinate = landmark_tuple[idx]
          to_coordinate = landmark_tuple[idx + 1]
          routes[idx] = from_coordinate

        for idx in range(24, 27): # 24, 25
          from_coordinate = landmark_tuple[idx]
          to_coordinate = landmark_tuple[idx + 1]
          routes[idx] = from_coordinate

        routes_line = list(routes.values())

        img_line = img.copy()
        cv2_utils.cv2_line_all_points(img_line, routes_line)

        imgs.append(img_line)
        merged_pil = pil_utils.merge_image_np(imgs, nrow=len(imgs), pad=1, channel_first=False)
        st.subheader('Landmarks face:')
        st_utils.st_image(merged_pil, caption=f"{merged_pil.size}", debug=global_cfg.tl_debug)

        # mask
        mask, img_mask = cv2_utils.get_mask_from_points(img, points=routes_line)

        # convex hull
        img_hull = img.copy()
        imgs = [img_line, ]
        face_landmarks = np.array(face_landmarks).reshape((-1, 1, 2))
        hull = cv2.convexHull(face_landmarks)
        hull = hull.squeeze()
        cv2_utils.cv2_line_all_points(img_hull, points=hull)
        imgs.append(img_hull)
        merged_pil = pil_utils.merge_image_np(imgs, nrow=len(imgs), pad=1, channel_first=False)
        st_utils.st_image(merged_pil, caption=f"{merged_pil.size}", debug=global_cfg.tl_debug)

        mask, img_hull_mask = cv2_utils.get_mask_from_points(img, points=hull)
        imgs = [img_mask, img_hull_mask]
        merged_pil = pil_utils.merge_image_np(imgs, nrow=len(imgs), pad=1, channel_first=False)
        st_utils.st_image(merged_pil, caption=f"{merged_pil.size}", debug=global_cfg.tl_debug)

    pass



