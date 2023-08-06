###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

import numpy as np
import pandas as pd
import os
import json
from scivae import VAE
from scircm import SciRCM

from sciutil import SciUtil, SciException
from sklearn.preprocessing import MinMaxScaler


class SciRCMException(SciException):
    def __init__(self, message=''):
        Exception.__init__(self, message)


class Vis:

    def __init__(self, scircm: SciRCM, output_dir=""):
        self.rcm = scircm
        self.output_dir = output_dir

