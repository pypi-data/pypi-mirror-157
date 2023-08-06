import numpy as np
from matplotlib.ticker import MaxNLocator
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path


colors_dict = {
  'dark_red': '#FF0000',
  'beauty_green': '#33E69C',
  'blue': '#2B99F0',
  'black': '#020202',
  'pink': '#FD4BD7',

  'red': '#FE2224',
  'green': '#17CE11',
  'dark_green': '#17CE11',
  'blue_violet': '#7241BE',
  'grey': '#A6A6A6',
  'peach': '#FEAA92',
  'yellow': '#FEFF00',
  'purple': '#A40190',
  'beauty_blue': '#1F5CFA',
  'beauty_light_blue': '#0CE6DA',
  'beauty_red': '#F84D4D',
  'beauty_orange': '#FF743E',
}


def fig_to_pil(fig):
  fig.canvas.draw()
  fig_pil = Image.frombytes('RGB',
                            fig.canvas.get_width_height(),
                            fig.canvas.tostring_rgb())
  return fig_pil


def ax_set_title(ax,
                 title,
                 fontsize=10):
  ax.set_title(title, fontsize=fontsize)
  pass

def ax_set_xlim(ax, xlim):
  ax.set_xlim(xlim)

def ax_set_ylim(ax, ylim):
  ax.set_ylim(ylim)

def set_ticks_number(ax,
                     N_ticks):
  ax.xaxis.set_major_locator(MaxNLocator(N_ticks))
  ax.yaxis.set_major_locator(MaxNLocator(N_ticks))
  pass

def ax_ticksize(ax, fontsize=10):
  ax.tick_params(labelsize=fontsize)
  pass


def ax_set_xticks(ax,
                  ticks,
                  num_ticks=None,
                  fontsize=10,
                  tick_labels=None):
  if num_ticks is not None:
    ticks = ticks[::len(ticks) // num_ticks] + [ticks[-1]]
  ax.set_xticks(ticks)
  ax.tick_params(labelsize=fontsize)

  if tick_labels:
    ax.set_xticklabels(tick_labels)
  pass

def ax_set_yticks(ax,
                  ticks):
  ax.set_yticks(ticks)
  pass

def ax_set_xlabel(ax,
                  xlabel,
                  fontsize=20):
  ax.set_xlabel(xlabel, fontsize=fontsize)
  pass

def ax_set_ylabel(ax,
                  ylabel,
                  fontsize=20):
  ax.set_ylabel(ylabel, fontsize=fontsize)
  pass


def get_fig_ax(nrows=1,
               ncols=1,
               style='seaborn-paper',
               usetex=False,
               add_grid=True,
               figsize=None):
  """

  :param nrows:
  :param ncols:
  :param style:  seaborn-paper seaborn-whitegrid
  :param usetex:
  :param figsize: (6.4, 4.4)
  :return:
  """
  import matplotlib.pyplot as plt

  plt.style.use(style)

  set_times_new_roman_font(usetex=usetex)
  fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)

  if nrows * ncols > 1:
    ax = list(ax.flatten())
  if add_grid:
    ax_add_grid(axs=ax)

  return fig, ax


def ax_add_grid(axs, alpha=0.2, linestyle='--'):
  if not isinstance(axs, list):
    axs = [axs]
  for ax in axs:
    ax.grid(b=True, which='major', color='#666666', linestyle=linestyle, alpha=alpha)
  pass

def set_times_new_roman_font(usetex=False):
  """
  sudo apt install ttf-mscorefonts-installer
  rm ~/.cache/matplotlib -rf

  :param usetex:
  :return:
  """
  if usetex and matplotlib.checkdep_usetex(True):
    # ax.plot(dim_emb_list, cos_ab_list, label=r"\textbf{\textit{d}(a, b)}")
    # activate latex text rendering
    from matplotlib import rc
    # rc('text', usetex=True)
    plt.rcParams['text.usetex'] = True

  plt.rcParams["font.family"] = "Times New Roman"
  plt.rcParams["mathtext.fontset"] = "cm"




def set_non_gui_backend(plt, ):
  try:
    fig = plt.figure()
  except:
    plt.switch_backend('agg')


def ax_legend(ax,
              font_size=20,
              loc='lower right',
              ncol=1,
              framealpha=1):
  ax.legend(prop={'size': font_size}, ncol=ncol, loc=loc, framealpha=framealpha)
  pass


def savefig(saved_file,
            fig,
            pad_inches=0.0,
            debug=False,
            axes_pad=None):


  print(f'Saved to {saved_file}')
  saved_file = Path(saved_file)
  saved_file_pdf = f"{saved_file.parent}/{saved_file.stem}.pdf"
  saved_file_png = f"{saved_file.parent}/{saved_file.stem}.png"


  if axes_pad:
    fig.tight_layout(pad=axes_pad)
  else:
    fig.tight_layout()

  fig.savefig(saved_file_png, bbox_inches='tight', pad_inches=0.1)
  fig.savefig(saved_file_pdf, bbox_inches='tight', pad_inches=pad_inches)

  # fig.show()
  fig.clear()
  if debug:
    img_pil = Image.open(saved_file_png).convert('RGB')
    plt.imshow(img_pil)
    plt.show()
  pass


def get_colors_by_cmap(N_colors,
                       cmap='rainbow',
                       uint8=True):
  if cmap == 'rainbow':
    cmap = matplotlib.cm.rainbow
  else:
    cmap = matplotlib.cm.jet
    
  colors = cmap(np.linspace(0, 1, N_colors))
  if uint8:
    colors = (colors * 255).astype(np.uint8)
  return colors