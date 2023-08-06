import os
import sys
import unittest


class Testing_dlib_web(unittest.TestCase):

  def test_align_face(self, debug=True):
    """
    Usage:

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=.:./tl2_lib
        python -c "from tl2_lib.tl2.proj.dlib.tests.test_dlib import Testing_dlib_web;\
          Testing_dlib_web().test_align_face(debug=False)" \
          --tl_opts port 8503

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file tl2_lib/tl2/proj/dlib/configs/dlib_web.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))

    script = "tl2_lib/tl2/proj/streamlit/scripts/run_web.py"
    if debug:
      cmd_str = f"""
          python 
            {script}
            {get_append_cmd_str(args)}
            --tl_debug
            --tl_opts
              """
    else:
      cmd_str_prefix = f"""
              {os.path.dirname(sys.executable)}/streamlit run --server.port {cfg.port} 
              {script}
              --
            """
      cmd_str = f"""
          {cmd_str_prefix}
            {get_append_cmd_str(args)}
            --tl_opts {tl_opts}
        """
    start_cmd_run(cmd_str)
    pass

  def test__convexHull(self, debug=True):
    """
    Usage:

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=.:./tl2_lib
        python -c "from tl2_lib.tl2.proj.dlib.tests.test_dlib import Testing_dlib_web;\
          Testing_dlib_web().test_crop_face_by_landmarks(debug=False)" \
          --tl_opts port 8561

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')

    import cv2
    import numpy as np
    from tl2.proj.cv2 import cv2_utils

    import cv2

    # 读取图片并转至灰度模式
    imagepath = 'tl2_lib/tl2/proj/dlib/datasets/hand_convex_hull.jpg'
    img = cv2.imread(imagepath, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化，取阈值为235
    ret, thresh = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY)

    # 寻找图像中的轮廓
    contours, hierarchy = cv2.findContours(thresh, 2, 1)

    # 寻找物体的凸包并绘制凸包的轮廓
    for cnt in contours:
      # cnt: (num_points, 1, 2)
      hull = cv2.convexHull(cnt)
      length = len(hull)
      # 如果凸包点集中的点个数大于5
      if length > 5:
        # 绘制图像凸包的轮廓
        for i in range(length):
          cv2.line(img, tuple(hull[i][0]), tuple(hull[(i + 1) % length][0]), (0, 0, 255), 2)

    cv2_utils.imshow_pil(img, is_bgr=True)
    pass

  def test_crop_face_by_landmarks(self, debug=True):
    """
    Usage:

        export CUDA_VISIBLE_DEVICES=0
        export TIME_STR=1
        export PYTHONPATH=.:./tl2_lib
        python -c "from tl2_lib.tl2.proj.dlib.tests.test_dlib import Testing_dlib_web;\
          Testing_dlib_web().test_crop_face_by_landmarks(debug=False)" \
          --tl_opts port 8561

    :return:
    """
    if 'CUDA_VISIBLE_DEVICES' not in os.environ:
      os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    if 'TIME_STR' not in os.environ:
      os.environ['TIME_STR'] = '0'
    from tl2 import tl2_utils
    from tl2.launch.launch_utils import \
      (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

    tl_opts_list = tl2_utils.parser_args_from_list(name="--tl_opts", argv_list=sys.argv, type='list')
    tl_opts = ' '.join(tl_opts_list)
    print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file tl2_lib/tl2/proj/dlib/configs/dlib_web.yaml
                --tl_command {command}
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))

    script = "tl2_lib/tl2/proj/streamlit/scripts/run_web.py"
    if debug:
      cmd_str = f"""
          python 
            {script}
            {get_append_cmd_str(args)}
            --tl_debug
            --tl_opts
              """
    else:
      cmd_str_prefix = f"""
              {os.path.dirname(sys.executable)}/streamlit run --server.port {cfg.port} 
              {script}
              --
            """
      cmd_str = f"""
          {cmd_str_prefix}
            {get_append_cmd_str(args)}
            --tl_opts {tl_opts}
        """
    start_cmd_run(cmd_str)
    pass


