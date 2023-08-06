from pathlib import Path
import sys
import pickle
# import matplotlib
# matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import unittest


class PlotResults(object):
    
    def __init__(self, ):
        # PlotResults.setup_env()
        
        pass
    
    @staticmethod
    def setup_env():
        import os
        try:
            import mpld3
        except:
            os.system('pip install mpld3')
    
    def get_last_md_inter_time(self, filepath):
        from datetime import datetime, timedelta

        modi_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        modi_inter = datetime.now() - modi_time
        modi_minutes = modi_inter.total_seconds() // 60
        return int(modi_minutes)
    
    def get_fig_axes(self,
                     rows,
                     cols,
                     figsize_wh=(15, 7),
                     style="seaborn-whitegrid"):
        import matplotlib.pyplot as plt
        # plt.style.use('ggplot')
        plt.style.use(style)
        plt.rcParams['axes.prop_cycle'] = plt.cycler(
            color=['blue',
                   'green',
                   'red',
                   'cyan',
                   'magenta',
                   'black',
                   'orange',
                   'lime',
                   'tan',
                   'salmon',
                   'gold',
                   'darkred',
                   'darkblue'])
        fig, axes = plt.subplots(rows, cols, figsize=(figsize_wh[0]*cols, figsize_wh[1]*rows))
        if rows * cols > 1:
            axes = axes.ravel()
        else:
            axes = [axes]
        return fig, axes
    
    def get_itr_val_str(self, data, ismax):
        if ismax:
            itr = int(data[:, 0][data[:, 1].argmax()])
            val = data[:, 1].max()
            return f'itr.{itr:06d}_maxv.{val:.3f}'
        else:
            itr = int(data[:, 0][data[:, 1].argmin()])
            val = data[:, 1].min()
            return f'itr.{itr:06d}_minv.{val:.3f}'

    def _data_load_func(self, filepath):
        data = np.loadtxt(filepath, delimiter=':')
        data = data.reshape(-1, 2)
        return data

    def plot_defaultdicts(self, outfigure, default_dicts, show_max=True, figsize_wh=(15, 8), legend_size=12,
                          dpi=500, data_load_func=None):

        import tempfile
        if not isinstance(show_max, list):
            show_max = [show_max]
        assert len(show_max) == len(default_dicts)

        fig, axes = self.get_fig_axes(rows=len(default_dicts), cols=1, figsize_wh=figsize_wh)

        if data_load_func is None:
            data_load_func_list = [self._data_load_func, ] * len(default_dicts)
        elif not isinstance(data_load_func, (list, tuple)):
            data_load_func_list = [data_load_func, ] * len(default_dicts)
        else:
            data_load_func_list = data_load_func

        label2datas_list = {}
        for idx, (dict_name, default_dict) in enumerate(default_dicts.items()):
            data_xlim = None
            axes_prop = default_dict.get('properties')
            if axes_prop is not None:
              if 'xlim' in axes_prop:
                data_xlim = axes_prop['xlim'][-1]

            label2datas = {}
            # for each result dir
            for (result_dir, label2file) in default_dict.items():
                if result_dir == 'properties':
                    continue
                # for each texlog file
                for label, file in label2file.items():
                    filepath = os.path.join(result_dir, file)
                    if not os.path.exists(filepath):
                      print(f'Not exist {filepath}, skip.')
                      continue
                    # get modified time
                    modi_minutes = self.get_last_md_inter_time(filepath)

                    data = data_load_func_list[idx](filepath)
                    # data = np.loadtxt(filepath, delimiter=':')
                    # data = data.reshape(-1, 2)
                    # limit x in a range
                    if data_xlim:
                      data = data[data[:, 0] <= data_xlim]
                    
                    itr_val_str = self.get_itr_val_str(data, show_max[idx])
                    label_str = f'{itr_val_str}' + f'-{modi_minutes:03d}m---' + label
                    
                    axes[idx].plot(data[:, 0], data[:, 1], label=label_str, marker='.', linewidth='5', markersize='10', alpha=0.5)
                    label2datas[label] = data
            axes[idx].legend(prop={'size': legend_size})
            axes[idx].set(**default_dict['properties'])
            axes[idx].grid(visible=True, which='major', color='#666666', linestyle='--', alpha=0.2)
                    
            label2datas_list[dict_name] = label2datas
        fig.show()
        fig.savefig(outfigure, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
        return label2datas_list

    def plot_results_pkl(self,
                         outfigure,
                         results_pkl,
                         show_max=[True],
                         figsize_wh=(15, 8),
                         legend_size=12,
                         dpi=500,
                         ):
      results_pkl = Path(results_pkl)
      title = results_pkl.stem

      with open(results_pkl, 'rb') as f:
        default_dicts = pickle.load(f)

      if len(show_max) != len(default_dicts):
        show_max = show_max * len(default_dicts)
      assert len(show_max) == len(default_dicts)

      fig, axes = self.get_fig_axes(rows=len(default_dicts), cols=1, figsize_wh=figsize_wh)

      label2datas_list = {}
      # for each subfigure
      for idx, (dict_name, default_dict) in enumerate(default_dicts.items()):
        label2datas = {}
        # for each line
        print(f"\n{dict_name}: ")
        for (data_name, data) in default_dict.items():

          itr_val_str = self.get_itr_val_str(data, show_max[idx])
          label_str = f'{itr_val_str}---' + data_name

          axes[idx].plot(data[:, 0],
                         data[:, 1],
                         label=label_str,
                         marker='.',
                         linewidth='5',
                         markersize='10',
                         alpha=0.5)
          print(data_name)
          label2datas[data_name] = data
        axes[idx].legend(prop={'size': legend_size})
        axes[idx].set_ylabel(dict_name, fontsize=20)
        axes[idx].grid(b=True, which='major', color='#666666', linestyle='--', alpha=0.2)

        label2datas_list[dict_name] = label2datas
      axes[0].set(title=title)
      fig.show()
      print(f'Saved to {outfigure}')
      fig.savefig(outfigure, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
      return label2datas_list


class TestingPlot(unittest.TestCase):

    def test__plot_text(self):
        """
        python -c "from exp.tests.test_styleganv2 import Testing_stylegan2_style_position;\
          Testing_stylegan2_style_position().test_plot_FID_cifar10_style_position()"
        """
        if 'CUDA_VISIBLE_DEVICES' not in os.environ:
            os.environ['CUDA_VISIBLE_DEVICES'] = '3'
        if 'TIME_STR' not in os.environ:
            os.environ['TIME_STR'] = '0'
        from tl2.launch.launch_utils import \
            (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

        command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
        argv_str = f"""
                      --tl_config_file none
                      --tl_command none
                      --tl_outdir {outdir}
                      """
        args = setup_outdir_and_yaml(argv_str)
        outdir = args.tl_outdir

        from tl2.proj.matplot.plot_results import PlotResults
        import collections
        import pickle

        outfigure = os.path.join(outdir, 'IS.jpg')
        default_dicts = collections.OrderedDict()
        show_max = []

        FID_FFHQ = collections.defaultdict(dict)
        title = 'FID_FFHQ'
        log_file = 'textdir/eval.ma0.fid.log'
        dd = eval(title)
        dd['results/train_ffhq/train_ffhq-20210712_223319_587/'] = \
            {'20210712_223319_587-pi_gan': f"{log_file}", }
        dd['results/nerf_inr_ffhq/train_ffhq-20210716_205928_189/'] = \
            {'20210716_205928_189-nerf_inr': f"{log_file}", }
        dd['results/nerf_inr_ffhq_v1/train_ffhq-20210717_221038_606/'] = \
            {'20210717_221038_606-nerf_inr_v1': f"{log_file}", }
        dd['results/nerf_inr_ffhq_v2/train_ffhq-20210718_145212_513/'] = \
            {'20210718_145212_513-nerf_inr_v2': f"{log_file}", }

        dd['properties'] = {'title': title, }
        default_dicts[title] = dd
        show_max.append(False)

        plotobs = PlotResults()
        label2datas_list = plotobs.plot_defaultdicts(
            outfigure=outfigure, default_dicts=default_dicts, show_max=show_max, figsize_wh=(16, 7.2))
        print(f'Save to {outfigure}.')

        saved_data = '__'.join(outdir.split('/')[-2:])
        saved_data = f"{outdir}/{saved_data}.pkl"
        with open(saved_data, 'wb') as f:
            pickle.dump(label2datas_list, f)
        print(f"Save data to {saved_data}")
        pass

    def test__plot_text_bucket(self):
      """
      python -c "from exp.tests.test_styleganv2 import Testing_stylegan2_style_position;\
        Testing_stylegan2_style_position().test_plot_FID_cifar10_style_position()"
      """
      if 'CUDA_VISIBLE_DEVICES' not in os.environ:
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
      if 'TIME_STR' not in os.environ:
        os.environ['TIME_STR'] = '0'
      from tl2.launch.launch_utils import \
        (get_command_and_outdir, setup_outdir_and_yaml, get_append_cmd_str, start_cmd_run)

      command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
      argv_str = f"""
                    --tl_config_file none
                    --tl_command none
                    --tl_outdir {outdir}
                    """
      args = setup_outdir_and_yaml(argv_str)
      outdir = args.tl_outdir

      from tl2.proj.matplot.plot_results import PlotResults
      import collections
      import pickle

      outfigure = os.path.join(outdir, 'FID.jpg')
      default_dicts = collections.OrderedDict()
      show_max = []

      bucket_root = "/home/ma-user/work/ZhouPeng/bucket_3690/"

      FID_FFHQ_r128 = collections.defaultdict(dict)
      title = 'FID_FFHQ_r128'
      log_file = 'textdir/eval.ma0.FID.log'
      dd = eval(title)
      dd[f'{bucket_root}/results/stylegan3-exp/encoder_inr_train_v2/train_ffhq_r256_softplus-20211222_120944_857'] = \
        {'20211222_120944_857-3dmm_210': f"{log_file}", }

      dd['properties'] = {'title': title,
                          # 'xlim': [0, 3000000],
                          # 'ylim': [0, 100]
                          }
      default_dicts[title] = dd
      show_max.append(False)

      plotobs = PlotResults()
      label2datas_list = plotobs.plot_defaultdicts(
        outfigure=outfigure, default_dicts=default_dicts, show_max=show_max, figsize_wh=(16, 7.2))
      print(f'Save to {outfigure}.')

      saved_data = '__'.join(outdir.split('/')[-2:])
      saved_data = f"{outdir}/{saved_data}.pkl"
      with open(saved_data, 'wb') as f:
        pickle.dump(label2datas_list, f)
      print(f"Save data to {saved_data}")
      pass

    def test_plot_results_pkl(self, debug=True):
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

      n_gpus = len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))
      PORT = os.environ.get('PORT', 8888)

      import pickle
      from tl2.proj.matplot.plot_results import PlotResults

      results_pkl = "datasets/results/OmniGAN_ImageNet128_results.pkl"

      outfigure = os.path.join(args.tl_outdir, 'FID_IS.jpg')
      plot_obs = PlotResults()
      show_max = [False, True]
      label2datas_list = plot_obs.plot_results_pkl(
        outfigure=outfigure,
        results_pkl=results_pkl,
        show_max=show_max,
        figsize_wh=(16, 7.2))

      pass


    def test_plot_figure(self):
      """
      Usage:
          export TIME_STR=1
          export PYTHONPATH=./exp:./BigGAN_PyTorch_1_lib:./
          python -c "from exp.tests.test_BigGAN_v1 import Testing_Figures;\
            Testing_Figures().test_save_early_collapse_on_cifar100()"

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

      command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
      argv_str = f"""
                    --tl_config_file tl2_lib/tl2/proj/matplot/configs/Plot.yaml
                    --tl_command {command}
                    --tl_outdir {outdir}
                    --tl_opts {tl_opts}
                    """
      args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

      import matplotlib.pyplot as plt
      import numpy as np
      import pickle
      import pathlib
      from tl2.proj.matplot import plt_utils

      fig, ax = plt_utils.get_fig_ax(style='seaborn-paper')
      # fig, ax = plt.subplots()

      # ax.set_xticks(range(0, 600, 100))
      ax.tick_params(labelsize=cfg.fontsize.tick_fs)
      ax.set_xlabel(cfg.xlabel, fontsize=cfg.fontsize.xylabel_fs)
      ax.set_ylabel(cfg.ylabel, fontsize=cfg.fontsize.xylabel_fs)

      properties = cfg.get('properties', {})
      ax.set(**properties)
      for idx, (_, data_dict) in enumerate(cfg.lines.items()):
        with open(data_dict.pkl_file, 'rb') as f:
          loaded_data = pickle.load(f)
        data = loaded_data[data_dict.dict_index][data_dict.data_index]

        if 'clip_x' in cfg:
          data_xlim = cfg.clip_x[-1]
          data = data[data[:, 0] <= data_xlim]

        if 'clip_x' in data_dict.properties:
          data_xlim = data_dict.properties.clip_x[-1]
          data_dict.properties.pop('clip_x')
          data = data[data[:, 0] <= data_xlim]

        if cfg.get_min_value:
          best_index = data[:, 1].argmin()
        else:
          best_index = data[:, 1].argmax()
        best_x = int(data[:, 0][best_index])
        best_y = data[:, 1][best_index]

        if cfg.add_auxi_label:
          data_dict.properties.label = f'x_{best_x}-y_{best_y:.3f}-' + getattr(data_dict.properties, 'label', '')

        linestyle = data_dict.properties.pop('ls', 'solid')
        if linestyle.startswith('('):
          linestyle = eval(linestyle)

        ax.plot(data[:, 0], data[:, 1], color=plt_utils.colors_dict[data_dict.color], ls=linestyle,
                **data_dict.properties)
        pass

      plt_utils.ax_legend(ax, font_size=cfg.fontsize.legend_size, loc="upper right")

      saved_file = os.path.join(args.tl_outdir, cfg.saved_file)
      plt_utils.savefig(saved_file, fig=fig, debug=True)

      pass

    def test_plot_figure_smooth(self):
      """
      Usage:
          export TIME_STR=1
          export PYTHONPATH=./exp:./BigGAN_PyTorch_1_lib:./
          python -c "from exp.tests.test_BigGAN_v1 import Testing_Figures;\
            Testing_Figures().test_save_early_collapse_on_cifar100()"

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

      command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
      argv_str = f"""
                  --tl_config_file tl2_lib/tl2/proj/matplot/configs/Plot.yaml
                  --tl_command {command}
                  --tl_outdir {outdir}
                  --tl_opts {tl_opts}
                  """
      args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

      import numpy as np
      import pickle
      import pathlib
      from tl2.proj.matplot import plt_utils
      from tsmoothie.smoother import LowessSmoother, ExponentialSmoother

      fig, ax = plt_utils.get_fig_ax(style='seaborn-paper')
      # fig, ax = plt.subplots()

      # ax.set_xticks(range(0, 600, 100))
      ax.tick_params(labelsize=cfg.fontsize.tick_fs)
      ax.set_xlabel(cfg.xlabel, fontsize=cfg.fontsize.xylabel_fs)
      ax.set_ylabel(cfg.ylabel, fontsize=cfg.fontsize.xylabel_fs)

      properties = cfg.get('properties', {})
      ax.set(**properties)
      for idx, (_, data_dict) in enumerate(cfg.lines.items()):
        with open(data_dict.pkl_file, 'rb') as f:
          loaded_data = pickle.load(f)
        data = loaded_data[data_dict.dict_index][data_dict.data_index]

        if 'clip_x' in cfg:
          data_xlim = cfg.clip_x[-1]
          data = data[data[:, 0] <= data_xlim]

        if 'clip_x' in data_dict.properties:
          data_xlim = data_dict.properties.clip_x[-1]
          data_dict.properties.pop('clip_x')
          data = data[data[:, 0] <= data_xlim]

        if cfg.get_min_value:
          best_index = data[:, 1].argmin()
        else:
          best_index = data[:, 1].argmax()
        best_x = int(data[:, 0][best_index])
        best_y = data[:, 1][best_index]

        if cfg.add_auxi_label:
          data_dict.properties.label = f'x_{best_x}-y_{best_y:.3f}-' + getattr(data_dict.properties, 'label', '')

        smoother = ExponentialSmoother(window_len=40, alpha=0.3)
        smoother.smooth(data[:, 1])
        low, up = smoother.get_intervals('sigma_interval')

        y = smoother.smooth_data[0]
        x = data[-len(y):, 0]
        linestyle = data_dict.properties.pop('ls', 'solid')
        if linestyle.startswith('('):
          linestyle = eval(linestyle)

        ax.plot(x, y, color=plt_utils.colors_dict[data_dict.color], ls=linestyle, **data_dict.properties)
        # ax.plot(x, y, '.k')
        ax.fill_between(x, low[0], up[0], alpha=0.3, color=plt_utils.colors_dict[data_dict.color])
        pass

      plt_utils.ax_legend(ax, font_size=cfg.fontsize.legend_size, loc="upper right")

      saved_file = os.path.join(args.tl_outdir, cfg.saved_file)
      plt_utils.savefig(saved_file, fig=fig, debug=True)

      pass

    def test__plot_smooth_figure(self):
      """
      Usage:
          export TIME_STR=1
          export PYTHONPATH=./exp:./BigGAN_PyTorch_1_lib:./
          python -c "from exp.tests.test_BigGAN_v1 import Testing_Figures;\
            Testing_Figures().test_save_early_collapse_on_cifar100()"

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

      command, outdir = get_command_and_outdir(self, func_name=sys._getframe().f_code.co_name, file=__file__)
      argv_str = f"""
                    --tl_config_file none
                    --tl_command none
                    --tl_outdir {outdir}
                    --tl_opts {tl_opts}
                    """
      args, cfg = setup_outdir_and_yaml(argv_str, return_cfg=True)

      import numpy as np
      import matplotlib.pyplot as plt
      from tsmoothie.utils_func import sim_randomwalk
      from tsmoothie.smoother import LowessSmoother, ExponentialSmoother
      from tl2.proj.matplot import plt_utils

      fig, axs = plt_utils.get_fig_ax(nrows=3, ncols=1, style='seaborn-paper')

      # generate 3 randomwalks of lenght 200
      np.random.seed(123)
      data = sim_randomwalk(n_series=3, timesteps=200,
                            process_noise=10, measure_noise=30)

      # operate smoothing
      # smoother = LowessSmoother(smooth_fraction=0.1, iterations=1)
      # smoother.smooth(data)
      # low, up = smoother.get_intervals('prediction_interval')

      smoother = ExponentialSmoother(window_len=40, alpha=0.3)
      smoother.smooth(data)
      low, up = smoother.get_intervals('sigma_interval')

      smooth_data = smoother.smooth_data

      # plot the smoothed timeseries with intervals
      for i in range(3):
        axs[i].plot(smooth_data[i], linewidth=3, color='blue')
        axs[i].plot(smoother.data[i], '.k')

        axs[i].set(title=f"timeseries {i + 1}")
        axs[i].set_xlabel('time')

        # x = data[-len(smoother.smooth_data[0]):, 0]
        x = range(len(smoother.data[i]))
        axs[i].fill_between(x, low[i], up[i], alpha=0.3)

      saved_file = os.path.join(args.tl_outdir, "fig.png")
      plt_utils.savefig(saved_file, fig=fig, debug=True)

      pass


