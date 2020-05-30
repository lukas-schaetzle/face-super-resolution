from enum import Enum
try:
  from jtop import jtop
except ModuleNotFoundError:
  pass

class Component(Enum):
  ALL = 'POM_5V_IN'
  CPU = 'POM_5V_CPU'
  GPU = 'POM_5V_GPU'

class ValueTypes(Enum):
  AVERAGE = 'avg'
  CURRENT = 'cur'

class JetsonMonitor:
  NO_DATA_DISPLAY = "N/A"

  def __init__(self):
    if jtop:
      self.jetson = jtop()
      self.jetson.open()
    else:
      self.jetson = None

  def get_power_usage(self, *args, **kwargs):
    if self.jetson:
      power_consumption_mw = self.jetson.stats["WATT"]
      return str(power_consumption_mw[component][type])
    else:
      return self.NO_DATA_DISPLAY

  def get_temp(self, *args, **kwargs):
    if self.jetson:
      return self.NO_DATA_DISPLAY
      # TODO
    else:
      return self.NO_DATA_DISPLAY

  def close():
    if self.jetson:
      self.jetson.close()
