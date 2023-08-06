import time
import shutil
from pathlib import Path
import logging
import os
import multiprocessing

from tl2.proj.pytorch.ddp import ddp_utils


def _copy_data(datapath_obs,
               datapath,
               overwrite=False,
               download=True,
               unzip=False):

  logger = logging.getLogger('tl')

  logger.info(f'=== {"Downloading" if download else "Uploading"} dataset ===')
  logger.info(f'=== from {datapath_obs} to \n {datapath} ===')
  try:
    import moxing as mox
    assert datapath_obs.startswith('s3://')

    datapath = os.path.expanduser(datapath)

    if download:
      if not mox.file.exists(datapath_obs):
        assert 0, datapath_obs

      if not overwrite and os.path.exists(datapath):
        logger.info(f'Exist. End copying [{datapath_obs}] \n to [{datapath}]')
        return

      if mox.file.is_directory(datapath_obs):
        # dir
        logger.info(f'Downloading dir [{datapath_obs}] \n to [{os.path.abspath(datapath)}]')
        mox.file.copy_parallel(datapath_obs, datapath)
      else:
        # file
        logger.info(f'Downloading file [{datapath_obs}] \n to [{os.path.abspath(datapath)}]')
        mox.file.copy(datapath_obs, datapath)
        if unzip:
          from tl2.tl2_utils import unzip_file
          logger.info(f'Unzipping file [{os.path.abspath(datapath)}] \n to [{os.path.dirname(datapath)}]')
          unzip_file(zip_file=datapath, dst_dir=os.path.dirname(datapath))
          logger.info("Done.")
      logger.info(f'End downloading [{datapath_obs}] \n to [{os.path.abspath(datapath)}]')
    else:
      # print('=== Uploading dataset ===')
      if os.path.isdir(datapath):
        # dir
        logger.info(f'Uploading dir [{datapath}] \n to [{datapath_obs}]')
        mox.file.copy_parallel(datapath, datapath_obs)
      else:
        # file
        logger.info(f'Uploading file [{datapath}] \n to [{datapath_obs}]')
        assert datapath_obs.endswith(os.path.basename(datapath))
        mox.file.copy(datapath, datapath_obs)
      logger.info(f'End uploading [{datapath}] \n to [{datapath_obs}]')

  except:
    logger = logging.getLogger('tl')
    # import traceback
    # logger.info('\n%s', traceback.format_exc())
    logger.info(f'\n\tRuning local. Ignore datapath: {datapath_obs}')

  pass

def copy_data(rank,
              global_cfg,
              datapath_obs,
              datapath,
              disable=False,
              overwrite=False,
              download=True,
              unzip=False,
              synchronize=True):
  """
  root_obs: &root_obs s3://bucket-3690/ZhouPeng

  obs_ffhq_r256: &obs_ffhq_r256
    datapath_obs: 'keras/ffhq/downsample_ffhq_256x256.zip'
    datapath: "datasets/ffhq/downsample_ffhq_256x256.zip"
    disable: false
    overwrite: false
    unzip: true

  :return:
  """
  if disable:
    return

  if not global_cfg.get('tl_mox', False):
    return

  if rank != 0:
    if synchronize: ddp_utils.d2_synchronize()
  else:

    datapath_obs = os.path.join(global_cfg.root_obs, datapath_obs)

    _copy_data(datapath_obs=datapath_obs, datapath=datapath, overwrite=overwrite,
               download=download, unzip=unzip)

    if synchronize: ddp_utils.d2_synchronize()
  print("")
  return


def moxing_copy_parallel(src_url,
                         dst_url,
                         create_base_dir=True):
  """
  Copy dir. copy xxx/data/ to dst/  (dst/data/)

  :param src_url:
  :param dst_url:
  :return:
  """
  import moxing

  if create_base_dir:
    base_dir = Path(src_url).name
    dst_url = f"{dst_url}/{base_dir}"

  print(f"Copy dir from {src_url} to \n\t{dst_url}")
  moxing.file.copy_parallel(src_url=src_url, dst_url=dst_url)
  pass


def moxing_copy(src_url,
                dst_url):
  """
  Copy a file. copy xxx/data.txt to dst/data.txt

  :param src_url:
  :param dst_url:
  :return:
  """
  import moxing

  if moxing.file.is_directory(dst_url):
    file_name = Path(src_url).name
    dst_url = f"{dst_url}/{file_name}"
  else:
    # assert moxing.file.exists(dst_url)
    pass

  print(f"Copy file from {src_url} to \n\t{dst_url}")
  moxing.file.copy(src_url=src_url, dst_url=dst_url)
  pass


def setup_tl_outdir_obs(cfg,
                        unzip_code=False):
  """
  Setup tl_outdir_obs
  Backup code.zip to tl_outdir
  """
  from tl2.tl2_utils import unzip_file

  if not cfg.get('tl_mox', False):
    return

  logger = logging.getLogger('tl')
  try:
    import moxing as mox
    # modelarts_record_jobs(args, myargs)
    logger.info(f"\n {'root_obs':<16}: {cfg.root_obs}")
    proj_dir = os.path.basename(os.path.abspath(os.path.curdir))
    assert cfg.tl_outdir.startswith('results/')
    cfg.tl_outdir_obs = os.path.join(cfg.root_obs, 'results', proj_dir, cfg.tl_outdir[8:])
    logger.info(f"\n {'tl_outdir':<16}: {cfg.tl_outdir}")
    logger.info(f"\n {'tl_outdir_obs':<16}: {cfg.tl_outdir_obs}")

    zip_code_file = cfg.get('zip_code_file', "code.zip")
    if os.path.exists(zip_code_file):
      os.makedirs(f'{cfg.tl_outdir}/code_bak', exist_ok=True)
      shutil.copy(zip_code_file, f'{cfg.tl_outdir}/code_bak')
      if unzip_code:
        unzip_file(zip_file=zip_code_file, dst_dir=f'{cfg.tl_outdir}/code_bak')
  except AttributeError:
    cfg.tl_mox = False
    print("Not set root_obs.")
  except ModuleNotFoundError:
    cfg.tl_mox = False
    import traceback
    traceback.print_exc()
  except:
    cfg.tl_mox = False
    import traceback
    traceback.print_exc()
  return



class CopyObsProcessing(multiprocessing.Process):
  """
    worker = CopyObsProcessing(args=(s, d, copytree))
    worker.start()
    worker.join()
  """
  def run(self):
    logger = logging.getLogger()
    try:
      import moxing as mox
      s, d, copytree = self._args
      logger.info('====== Starting %s, Copying %s to\n %s' % (self.name, s, d))
      start_time = time.time()
      if copytree:
        logger = logging.getLogger()
        logger.disabled = True
        mox.file.copy_parallel(s, d)
        logger = logging.getLogger()
        logger.disabled = False
      else:
        mox.file.copy(s, d)
      elapsed_time = time.time() - start_time
      time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
      logger.info('End %s, elapsed time: %s'%(self.name, time_str))
    except:
      import traceback
      logger.info(traceback.format_exc())
      # if str(e) == 'server is not set correctly':
      #   print(str(e))
      # else:
      #   print('Exception %s' % (self.name))
    return


def copy_obs_process(s,
                     d,
                     copytree=False,
                     join=False):

  worker = CopyObsProcessing(args=(s, d, copytree))
  worker.start()
  if join:
    worker.join()
  return


def modelarts_sync_results_dir(cfg,
                               join=False,
                               is_main_process=True,
                               sync_every_sec=90):

  if not cfg.get('tl_mox', False):
    return

  if not is_main_process:
    return

  if not join:
    now = time.time()
    tl_sync_last_time = getattr(cfg, 'tl_sync_last_time', 0)
    if now - tl_sync_last_time < sync_every_sec:
      return
    cfg.tl_sync_last_time = now

  logger = logging.getLogger('tl')
  logger.info(f'\n======Uploading results dir======')

  try:
    copy_obs_process(cfg.tl_outdir, cfg.tl_outdir_obs, copytree=True, join=join)
  except:
    import traceback
    logger.info(traceback.format_exc())

  logger.info(f'\n======End uploading results dir======')
  return
