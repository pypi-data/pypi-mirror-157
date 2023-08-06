from fvcore.common.timer import Timer as Timer_base

_Timer_dict = {}


class Timer(Timer_base):

  def __init__(self,
               time_interval=0):
    super(Timer, self).__init__()

    self.time_interval = time_interval
    pass

  def do(self):
    """
    Do if elapsed time > time_interval.

    """
    elapsed = self.seconds()
    if elapsed > self.time_interval:
      self.reset()
      return True
    else:
      return False

  @staticmethod
  def get_named_timer(name,
                      time_interval=0):

    if name not in _Timer_dict:
      timer = Timer(time_interval=time_interval)
      _Timer_dict[name] = timer
    else:
      timer = _Timer_dict[name]

    return timer

