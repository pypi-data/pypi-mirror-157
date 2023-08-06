import os
import sys
import unittest
import argparse


class Testing_einops(unittest.TestCase):

  def test_rearrange(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    from einops import rearrange, reduce, repeat
    from tl2.proj.pil import pil_utils

    ims = np.load('tl2_lib/tl2/proj/einops/resources/test_images.npy', allow_pickle=False)
    # There are 6 images of shape 96x96 with 3 color channels packed into tensor
    print(ims.shape, ims.dtype)
    # (6, 96, 96, 3) float64

    pil_utils.imshow_np(ims[0], range01=True, title='img[0]')

    # rearrange, as its name suggests, rearranges elements
    # below we swapped height and width.
    # In other words, transposed first two axes (dimensions)
    img = rearrange(ims[0], 'h w c -> w h c')
    pil_utils.imshow_np(img, range01=True, title='h w c -> w h c')

    # einops allows seamlessly composing batch and height to a new height dimension
    # We just rendered all images by collapsing to 3d tensor!
    img = rearrange(ims, 'b h w c -> (b h) w c')
    pil_utils.imshow_np(img, range01=True, title='b h w c -> (b h) w c')

    # or compose a new dimension of batch and width
    img = rearrange(ims, 'b h w c -> h (b w) c')
    pil_utils.imshow_np(img, range01=True, title='b h w c -> h (b w) c')

    # finally, combine composition and decomposition:
    img = rearrange(ims, '(b1 b2) h w c -> (b1 h) (b2 w) c', b1=2)
    pil_utils.imshow_np(img, range01=True, title='(b1 b2) h w c -> (b1 h) (b2 w) c')

    # slightly different composition: b1 is merged with width, b2 with height
    # ... so letters are ordered by w then by h
    img = rearrange(ims, '(b1 b2) h w c -> (b2 h) (b1 w) c ', b1=2)
    pil_utils.imshow_np(img, range01=True, title='(b1 b2) h w c -> (b2 h) (b1 w) c')

    # move part of width dimension to height.
    # we should call this width-to-height as image width shrunk by 2 and height doubled.
    # but all pixels are the same!
    # Can you write reverse operation (height-to-width)?
    img = rearrange(ims, 'b h (w w2) c -> (h w2) (b w) c', w2=2)
    pil_utils.imshow_np(img, range01=True, title='b h (w w2) c -> (h w2) (b w) c')

    # compare with the next example
    img = rearrange(ims, 'b h w c -> h (w b) c')
    pil_utils.imshow_np(img, range01=True, title='b h w c -> h (w b) c')

    # what if b1 and b2 are reordered before composing to width?
    img = rearrange(ims, '(b1 b2) h w c -> h (b1 b2 w) c ', b1=2)  # produces 'einops'
    pil_utils.imshow_np(img, range01=True, title='(b1 b2) h w c -> h (b1 b2 w) c ')
    img = rearrange(ims, '(b1 b2) h w c -> h (b2 b1 w) c ', b1=2)  # produces 'eoipns'
    pil_utils.imshow_np(img, range01=True, title='(b1 b2) h w c -> h (b2 b1 w) c ')

    pass

  def test_reduce(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    from einops import rearrange, reduce, repeat
    from tl2.proj.pil import pil_utils

    ims = np.load('tl2_lib/tl2/proj/einops/resources/test_images.npy', allow_pickle=False)
    # There are 6 images of shape 96x96 with 3 color channels packed into tensor
    print(ims.shape, ims.dtype)
    # (6, 96, 96, 3) float64

    pil_utils.imshow_np(ims[0], range01=True, title='img[0]')

    # if axis is not present in the output — you guessed it — axis was reduced
    # average over batch
    img = reduce(ims, 'b h w c -> h w c', 'mean')
    pil_utils.imshow_np(img, range01=True, title='b h w c -> h w c, mean')

    # this is mean-pooling with 2x2 kernel
    # image is split into 2x2 patches, each patch is averaged
    img = reduce(ims, 'b (h h2) (w w2) c -> h (b w) c', 'mean', h2=2, w2=2)
    pil_utils.imshow_np(img, range01=True, title='b (h h2) (w w2) c -> h (b w) c, mean_pooling 2x2')

    # yet another example. Can you compute result shape?
    img = reduce(ims, '(b1 b2) h w c -> (b2 h) (b1 w)', 'mean', b1=2)
    pil_utils.imshow_np(img, range01=True, title='(b1 b2) h w c -> (b2 h) (b1 w)')

    # compute max in each image individually, then show a difference
    tmp = reduce(ims, 'b h w c -> b () () c', 'max')
    x = reduce(ims, 'b h w c -> b () () c', 'max') - ims
    img = rearrange(x, 'b h w c -> h (b w) c')
    pil_utils.imshow_np(img, range01=True, title='b h w c -> h (b w) c, max - img')
    pass

  def test_stack_concatenate(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    from einops import rearrange, reduce, repeat
    from tl2.proj.pil import pil_utils

    ims = np.load('tl2_lib/tl2/proj/einops/resources/test_images.npy', allow_pickle=False)
    # There are 6 images of shape 96x96 with 3 color channels packed into tensor
    print(ims.shape, ims.dtype)
    # (6, 96, 96, 3) float64

    pil_utils.imshow_np(ims[0], range01=True, title='img[0]')

    # rearrange can also take care of lists of arrays with the same shape
    x = list(ims)
    print(type(x), 'with', len(x), 'tensors of shape', x[0].shape)
    # that's how we can stack inputs
    # "list axis" becomes first ("b" in this case), and we left it there
    img = rearrange(x, 'b h w c -> b h w c')

    # ... or we can concatenate along axes
    img = rearrange(x, 'b h w c -> h (b w) c')
    pass

  def test_expand_squeeze(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    from einops import rearrange, reduce, repeat
    from tl2.proj.pil import pil_utils

    ims = np.load('tl2_lib/tl2/proj/einops/resources/test_images.npy', allow_pickle=False)
    # There are 6 images of shape 96x96 with 3 color channels packed into tensor
    print(ims.shape, ims.dtype)
    # (6, 96, 96, 3) float64

    # functionality of numpy.expand_dims
    x = rearrange(ims, 'b h w c -> b 1 h w 1 c')
    print(x.shape)
    # functionality of numpy.squeeze
    print(rearrange(x, 'b 1 h w 1 c -> b h w c').shape)

    pass

  def test_repeat(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    from einops import rearrange, reduce, repeat
    from tl2.proj.pil import pil_utils

    ims = np.load('tl2_lib/tl2/proj/einops/resources/test_images.npy', allow_pickle=False)
    # There are 6 images of shape 96x96 with 3 color channels packed into tensor
    print(ims.shape, ims.dtype)
    # (6, 96, 96, 3) float64

    # repeat along a new axis. New axis can be placed anywhere
    img = repeat(ims[0], 'h w c -> h new_axis w c', new_axis=5)

    # shortcut
    img = repeat(ims[0], 'h w c -> h 5 w c')

    # repeat along w (existing axis)
    img = repeat(ims[0], 'h w c -> h (repeat w) c', repeat=3)
    pil_utils.imshow_np(img, range01=True, title='h w c -> h (3 w) c')

    # repeat along two existing axes
    img = repeat(ims[0], 'h w c -> (2 h) (2 w) c')
    pil_utils.imshow_np(img, range01=True, title='h w c -> (2 h) (2 w) c')

    # order of axes matters as usual - you can repeat each element (pixel) 3 times
    # by changing order in parenthesis
    img = repeat(ims[0], 'h w c -> h (w repeat) c', repeat=3)
    pil_utils.imshow_np(img, range01=True, title='h w c -> h (w 3) c')

    pass


class Testing_einops_DL(unittest.TestCase):

  def test_common_ops(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    from einops import rearrange, reduce, repeat
    import torch
    from tl2.proj.pil import pil_utils

    x = np.random.RandomState(42).normal(size=[10, 32, 100, 200])
    x = torch.from_numpy(x)
    x.requires_grad = True

    # flatten
    y = rearrange(x, 'b c h w -> b (c h w)')

    # space-to-depth
    y = rearrange(x, 'b c (h h1) (w w1) -> b (h1 w1 c) h w', h1=2, w1=2)

    # depth-to-space
    y = rearrange(x, 'b (c h1 w1) h w -> b c (h h1) (w w1)', h1=2, w1=2)

    # global average pooling
    y = reduce(x, 'b c h w -> b c', reduction='mean')

    # max-pooling with a kernel 2x2
    y = reduce(x, 'b c (h h1) (w w1) -> b c h w', reduction='max', h1=2, w1=2)
    y = reduce(x, 'b c (h 2) (w 2) -> b c h w', reduction='max')

    # 1D
    # reduce(x, '(t 2) b c -> t b c', reduction='max')

    # volumetric
    # reduce(x, 'b c (x 2) (y 2) (z 2) -> b c x y z', reduction='max')

    # per-channel mean-normalization
    y = x - reduce(x, 'b c h w -> b c 1 1', 'mean')

    # per-channel mean-normalization for whole batch
    y = x - reduce(y, 'b c h w -> 1 c 1 1', 'mean')

    list_of_tensors = list(x)

    # concatenate over the first dimension
    tensors = rearrange(list_of_tensors, 'b c h w -> (b h) w c')
    # or maybe concatenate along last dimension?
    tensors = rearrange(list_of_tensors, 'b c h w -> h w (b c)')

    # channel shuffle
    y = rearrange(x, 'b (g1 g2 c) h w-> b (g2 g1 c) h w', g1=4, g2=4)
    y = rearrange(x, 'b (g c) h w-> b (c g) h w', g=4)

    # Split a dimension
    # Assume we got 8 bboxes, 4 coordinates each.
    # To get coordinated into 4 separate variables, you move corresponding dimension to front and unpack tuple
    bbox_x, bbox_y, bbox_w, bbox_h = rearrange(x, 'b (coord bbox) h w -> coord b bbox h w', coord=4, bbox=8)
    # now you can operate on individual variables
    max_bbox_area = reduce(bbox_w * bbox_h, 'b bbox h w -> b h w', 'max')

    pass

  def test_parse_shape(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    from einops import rearrange, reduce, repeat
    from einops import parse_shape

    x = np.random.RandomState(42).normal(size=[10, 32, 100, 200])

    out = parse_shape(x, 'b c h w')
    out = parse_shape(x, 'b c _ _')
    pass

  def test_Layers(self, debug=True):
    """
    Usage:
        proj_root=pi-GAN-exp
        python tl2_lib/tl2/modelarts/scripts/copy_tool.py \
          -s s3://bucket-7001/ZhouPeng/codes/$proj_root -d /cache/$proj_root -t copytree -b /cache/$proj_root/code.zip
        cd /cache/$proj_root
        cp tl2_lib/tl2/modelarts/sources/pip.conf.modelarts /root/.pip/pip.conf
        cp tl2_lib/tl2/modelarts/sources/sources.list.modelarts /etc/apt/sources.list
        pip install -e tl2_lib

        export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
        export TIME_STR=1
        export PYTHONPATH=.
        python -c "from tl2.launch.tests.test_launch import Testing_Launch_v1;\
          Testing_Launch_v1().test_launch_ddp(debug=False)" \
          --tl_opts test0 10 test1 11 --test 1

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
    # tl_opts = ' '.join(sys.argv[sys.argv.index('--tl_opts') + 1:]) if '--tl_opts' in sys.argv else ''
    # print(f'tl_opts:\n {tl_opts}')

    command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
    argv_str = f"""
                --tl_config_file none
                --tl_command none
                --tl_outdir {outdir}
                --tl_opts {tl_opts}
                """
    args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

    import numpy as np
    import torch
    from torch.nn import Sequential, Conv2d, MaxPool2d, Linear, ReLU
    from einops.layers.torch import Reduce, Rearrange
    from einops import rearrange, reduce, repeat
    from einops import parse_shape
    from tl2.proj.pytorch.pytorch_hook import VerboseModel

    x = np.random.RandomState(42).normal(size=[10, 3, 20, 20])
    x = x.astype(np.float32)
    x = torch.from_numpy(x)

    tmp = rearrange(x, "b c h w -> b c (h w)")

    model = Sequential(
      Conv2d(3, 6, kernel_size=3, padding=1),
      MaxPool2d(kernel_size=2),
      Conv2d(6, 16, kernel_size=3, padding=1),
      # combined pooling and flattening in a single step
      Reduce('b c (h 2) (w 2) -> b (c h w)', 'mean'),
      Linear(16 * 5 * 5, 120),
      ReLU(),
      Linear(120, 10),
    )

    model_ver = VerboseModel(model, name_padding=15, input_padding=40, output_padding=40)
    out = model_ver(x)

    pass



















