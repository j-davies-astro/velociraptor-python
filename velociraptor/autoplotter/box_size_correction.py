"""
Functionality to apply a mass dependent correction to quantities that have been
binned in mass bins (e.g. a mass function).
"""

import numpy as np
import yaml
import os
import scipy.interpolate as interpol


class VelociraptorBoxSizeCorrection:
    def __init__(self, filename: str, correction_directory: str):
        correction_file = f"{correction_directory}/{filename}"
        if not os.path.exists(correction_file):
            raise FileNotFoundError(f"Could not find {correction_file}!")
        with open(correction_file, "r") as handle:
            correction_data = yaml.safe_load(handle)
        self.is_log_x = correction_data["is_log_x"]
        x = np.array(correction_data["x"])
        y = np.array(correction_data["y"])
        self.correction_spline = interpol.InterpolatedUnivariateSpline(x, y)

    def apply_mass_function_correction(self, mass_function_output):

        bin_centers, mass_function, error = mass_function_output

        if self.is_log_x:
            correction = self.correction_spline(np.log10(bin_centers))
        else:
            correction = self.correction_spline(bin_centers)

        corrected_mass_function = mass_function * correction
        corrected_mass_function.name = mass_function.name

        return bin_centers, corrected_mass_function, error
