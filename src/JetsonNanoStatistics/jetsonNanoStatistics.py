#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from jtop import jtop
import time
from enumComponent import Component
from enumValueTypes import ValueTypes

class JetsonNanoStatistics:
    def __init__(self):
        with jtop() as jetson:
            while True:
                self.__powerConsumptionInMilliwatts = jetson.stats["WATT"]
                """
                print(self.getPowerConsumptionInMilliwattsFor(Component.CPU.value, ValueTypes.AVERAGE.value))
                print(self.getPowerConsumptionInMilliwattsFor(Component.MAINBOARD.value, ValueTypes.AVERAGE.value))
                print(self.getPowerConsumptionInMilliwattsFor(Component.GPU.value, ValueTypes.AVERAGE.value))
                """

    """
    component - every possible component listed in enumComponent.py, e.g. Component.CPU.value to get the value of CPU
    type - possible value type defined in enumValueTypes.py, e.g. ValueTypes.AVERAGE.value for average power consumption
    """
    def getPowerConsumptionInMilliwattsFor(self, component, type):
        return self.__powerConsumptionInMilliwatts[component][type]
		
statistics = JetsonNanoStatistics()
# EOF
