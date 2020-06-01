from enum import Enum

try:
  from jtop import jtop
except ModuleNotFoundError:
  jtop = None

class PowerSensor(Enum):
  ALL = 'POM_5V_IN'
  CPU = 'POM_5V_CPU'
  GPU = 'POM_5V_GPU'

class ThermalSensor(Enum):
  ALWAYS_ON = 'AO'
  PLL = 'PLL'
  AVG_CPU_GPU = 'thermal'
  GPU = 'GPU'
  CPU = 'CPU'

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

  def get_power_usage(self, component=PowerSensor.ALL.value, type=ValueTypes.CURRENT.value):
    if self.jetson:
      power_consumption_mw = self.jetson.stats["WATT"]
      return str(power_consumption_mw[component][type])
    else:
      return self.NO_DATA_DISPLAY

  def get_temp(self, component=ThermalSensor.AVG_CPU_GPU.value):
    if self.jetson:
      thermal_celsius = self.jetson.stats["TEMP"]
      return str(thermal_celsius[component])
    else:
      return self.NO_DATA_DISPLAY

  def close(self):
    if self.jetson:
      self.jetson.close()
