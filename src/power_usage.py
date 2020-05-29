from enum import Enum

class Component(Enum):
  ALL = 'POM_5V_IN'
  CPU = 'POM_5V_CPU'
  GPU = 'POM_5V_GPU'

class ValueTypes(Enum):
  AVERAGE = 'avg'
  CURRENT = 'cur'

try:
  from jtop import jtop
except ModuleNotFoundError:
  def get_power_usage(*args, **kwargs):
    return "N/A"
else:
  def get_power_usage(component=Component.ALL, type=ValueTypes.CURRENT):
    with jtop() as jetson:
      power_consumption_mw = jetson.stats["WATT"]
      return power_consumption_mw[component][type]
