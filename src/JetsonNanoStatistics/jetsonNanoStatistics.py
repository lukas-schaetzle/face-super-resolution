# install package jetson stats:  sudo -H pip install -U jetson-stats

from jtop import jtop
import time
from enumComponent import Component
from enumValueTypes import ValueTypes

class JetsonNanoStatistics:
    def __init__(self):
        with jtop() as jetson:
            while True:
                self.__powerConsumptionInMilliwatts = jetson.stats["WATT"]
                
                print(self.getPowerConsumptionInMilliwattsFor(Component.CPU.value, ValueTypes.AVERAGE.value))
                print(self.getPowerConsumptionInMilliwattsFor(Component.MAINBOARD.value, ValueTypes.AVERAGE.value))
                print(self.getPowerConsumptionInMilliwattsFor(Component.GPU.value, ValueTypes.AVERAGE.value))

    """
    component - every possible component listed in enumComponent.py, e.g. Component.CPU.value to get the value of CPU
    type - possible value type defined in enumValueTypes.py, e.g. ValueTypes.AVERAGE.value for average power consumption
    """
    def getPowerConsumptionInMilliwattsFor(self, component, type):
        return self.__powerConsumptionInMilliwatts[component][type]
		
statistics = JetsonNanoStatistics()
