"""
CDR Helper Module
=====================

    This is just a small module to help people work with Call Detail Records
    (CDR). There are data generators to make fake CDRs as well as tools to help
    import and analyze data.
"""

#   ORDER MATTERS!
#   Keep it in this order to overwrite new NetworkX components code
from __future__ import absolute_import
import pandas as pd

from cdrhelper.generator import *
from cdrhelper.legacy import *
from cdrhelper.misc import *
from cdrhelper.importer import *
from cdrhelper.analyze import *

#   Prettier graph settings. Comment out if you don't want them.
pd.set_option('display.mpl_style', 'default')
