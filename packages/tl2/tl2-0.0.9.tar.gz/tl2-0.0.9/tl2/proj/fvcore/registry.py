import os
import sys
import unittest
import importlib
import logging
import copy
from typing import Dict, Optional
from fvcore.common.registry import Registry as Registry_base


class Registry(Registry_base):

  def _do_register(self, name: str, obj: object) -> None:
    # assert (
    #       name not in self._obj_map
    # ), "An object named '{}' was already registered in '{}' registry!".format(
    #   name, self._name
    # )

    if name in self._obj_map:
      print(f"An object named '{name}' was already registered in '{self._name}' registry! \n"
            f"Using old: {self._obj_map[name]}\n"
            f"Ignore new: {obj}\n")
      return
    # logging.getLogger('tl').warning(f"\n  {name} was already registered in {self._name} registry!")
    self._obj_map[name] = obj
    pass

  def register(self, obj: object = None, name=None, name_prefix=None) -> Optional[object]:
    """
    Register the given object under the the name `obj.__name__`.
    Can be used as either a decorator or not. See docstring of this class for usage.
    """
    if obj is None:
      # used as a decorator
      def deco(func_or_class: object, name=name, name_prefix=name_prefix) -> object:
        # name = func_or_class.__name__  # pyre-ignore
        if name is None:
          if name_prefix is None:
            name = f"{func_or_class.__module__}.{func_or_class.__name__}"
          else:
            name = f"{name_prefix}.{func_or_class.__name__}"
        else:
          name = name
        self._do_register(name, func_or_class)
        return func_or_class
      return deco
    # used as a function call
    self._do_register(name, obj)
    pass

  def clear(self):
    obj_map = self._obj_map
    self._obj_map = {}
    return obj_map

  def update(self, obj_map):
    self._obj_map.update(obj_map)

def build_from_cfg(cfg, registry, kwargs_priority, default_args=None):

  if not isinstance(cfg, dict):
    raise TypeError(f'cfg must be a dict, but got {type(cfg)}')
  if 'name' not in cfg:
    if default_args is None or 'type' not in default_args:
      raise KeyError(
        '`cfg` or `default_args` must contain the key "type", '
        f'but got {cfg}\n{default_args}')
  if not isinstance(registry, Registry):
    raise TypeError('registry must be an Registry object, '
                    f'but got {type(registry)}')
  if not (isinstance(default_args, dict) or default_args is None):
    raise TypeError('default_args must be a dict or None, '
                    f'but got {type(default_args)}')

  # cfg = cfg.clone()
  cfg = copy.deepcopy(cfg)
  if kwargs_priority:
    args = {**cfg, **default_args}
  else:
    args = {**default_args, **cfg}

  obj_type = args.pop('name')
  obj_cls = registry.get(obj_type)
  return obj_cls(**args)


REGISTRY = Registry("MODEL_REGISTRY")  # noqa F401 isort:skip
MODEL_REGISTRY = REGISTRY
REGISTRY.__doc__ = """

"""

def _register_modules(register_modules):
  for module in register_modules:
    importlib.import_module(module)
    # reload_module(module=module)
    # logging.getLogger('tl').info(f"  Register {module}")
  pass


def _build(cfg, kwargs_priority, cfg_to_kwargs, build_verbose=True, **kwargs):
    cfg = cfg.clone()

    _register_modules(register_modules=cfg.pop('register_modules', []))

    if build_verbose:
      logger = logging.getLogger('tl')
      logger.info(REGISTRY)
      logger.info(f"Build model:\n\t {cfg.name}")
      # print("")
    if not cfg_to_kwargs:
        ret = REGISTRY.get(cfg.name)(cfg=cfg, kwargs_priority=kwargs_priority, **kwargs)
    else:
        ret = build_from_cfg(cfg=cfg, registry=REGISTRY, kwargs_priority=kwargs_priority, default_args=kwargs)
    return ret


def build_model(cfg,
                kwargs_priority=False,
                cfg_to_kwargs=True,
                build_verbose=True,
                **kwargs):
    """
      register_modules:
        - "exp2.hrinversion.models.style_inr_gan"
      name: "exp2.hrinversion.models.style_inr_gan.GeneratorUltraZPC"
  
    :param cfg:
    :param kwargs_priority:
    :param cfg_to_kwargs:
    :param kwargs:
    :return:
    """
    return _build(cfg, kwargs_priority=kwargs_priority, cfg_to_kwargs=cfg_to_kwargs, build_verbose=build_verbose, **kwargs)



# MODULE_REGISTRY = Registry("MODULE_REGISTRY")  # noqa F401 isort:skip
# MODULE_REGISTRY.__doc__ = """
#
# """
def build_module(name):
  """
  register_module: ""

  :param cfg:
  :return:
  """
  logger = logging.getLogger('tl')
  logger.info(f"Building {name} ...")

  if name not in REGISTRY._obj_map:
    module = importlib.import_module(name)
    REGISTRY.register(obj=module, name=name)

  logger.info(REGISTRY)
  return REGISTRY.get(name=name)


