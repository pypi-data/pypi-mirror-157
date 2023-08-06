import logging
import pickle



def save_model(model, snapshot_pkl):
  logger = logging.getLogger('tl')
  logger.info(f"Save persistence model: {snapshot_pkl}")
  with open(snapshot_pkl, 'wb') as f:
    pickle.dump(model, f)

def load_model(snapshot_pkl):
  logger = logging.getLogger('tl')
  logger.info(f"Load persistence model: {snapshot_pkl}")
  with open(snapshot_pkl, 'rb') as f:
    net = pickle.load(f)
  return net





