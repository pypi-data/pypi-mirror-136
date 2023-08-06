"""splinecalib is a Python package for Probability Calibration
using smoothing splines."""

from .splinecalib import SplineCalib
from .calibration_utils import plot_prob_calibration,plot_reliability_diagram
from .calibration_utils import get_stratified_foldnums,cv_predictions
from .calibration_utils import my_logit, my_logistic


__version__ = '0.0.1'
