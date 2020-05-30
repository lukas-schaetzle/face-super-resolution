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

  def close_power_monitor():
    pass
else:
  jetson = jtop()
  jetson.open()

  def get_power_usage(component=Component.ALL.value, type=ValueTypes.CURRENT.value):
    power_consumption_mw = jetson.stats["WATT"]
    print(power_consumption_mw)
    return str(power_consumption_mw[component][type])

  def close_power_monitor():
    jetson.close()
