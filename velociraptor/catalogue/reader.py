import h5py
import os
import unyt


class VelociraptorCatalogueReader:
    def __init__(self, filename):
        with h5py.File(filename, "r") as handle:
            if "PseudoVR" in handle:
                self.type = "new"
            else:
                self.type = "old"

            self.filename = filename

    def get_name(self):
        return self.filename

    def is_old_catalogue(self):
        return self.type == "old"

    def get_run_information(self):
        assert self.type == "new"
        with h5py.File(self.filename, "r") as handle:
            cosmo = handle["SWIFT/Cosmology"].attrs
            a = cosmo["Scale-factor"][0]
            z = cosmo["Redshift"][0]
            H0 = cosmo["H0 [internal units]"][0]
            Omega_m = cosmo["Omega_m"][0]
            Omega_lambda = cosmo["Omega_lambda"][0]
            w0 = cosmo["w_0"][0]
            Omega_b = cosmo["Omega_b"][0]
            boxsize = handle["PseudoVR"].attrs["Boxsize_in_comoving_Mpc"] * unyt.Mpc
        physical_boxsize = a * boxsize
        return (
            {
                "a": a,
                "scale_factor": a,
                "z": z,
                "redshift": z,
                "mass": 1.0,
                "length": 1.0,
                "velocity": 1.0,
                "metallicity": 1.0,
                "age": 1.0,
                "star_formation_rate": 1.0,
                "box_length": boxsize,
                "comoving_box_volume": boxsize ** 3,
                "period": physical_boxsize,
                "physical_box_volume": physical_boxsize ** 3,
            },
            {
                "H0": H0,
                "Omega_m": Omega_m,
                "Omega_lambda": Omega_lambda,
                "w0": w0,
                "Omega_b": Omega_b,
            },
        )

    def get_datasets(self):
        with h5py.File(self.filename, "r") as handle:
            if self.type == "old":
                dsets = list(handle.keys())
            else:
                dsets = list(handle["PseudoVR"].keys())
        return dsets

    def unit_metadata(self, field):
        if self.type == "old":
            return None
        else:
            with h5py.File(self.filename, "r") as handle:
                field = f"PseudoVR/{field}"
                unitdict = dict(handle[field].attrs)
                factor = (
                    unitdict[
                        "Conversion factor to CGS (including cosmological corrections)"
                    ][0]
                    * unyt.A ** unitdict["U_I exponent"][0]
                    * unyt.cm ** unitdict["U_L exponent"][0]
                    * unyt.g ** unitdict["U_M exponent"][0]
                    * unyt.K ** unitdict["U_T exponent"][0]
                    * unyt.s ** unitdict["U_t exponent"][0]
                )
            return factor

    def read_field(self, field, mask, unit):
        with h5py.File(self.filename, "r") as handle:
            if self.type == "old":
                return unyt.unyt_array(handle[field][mask], unit)
            else:
                field = f"PseudoVR/{field}"
                data = handle[field][mask]
                unitdict = dict(handle[field].attrs)
                factor = (
                    unitdict[
                        "Conversion factor to CGS (including cosmological corrections)"
                    ][0]
                    * unyt.A ** unitdict["U_I exponent"][0]
                    * unyt.cm ** unitdict["U_L exponent"][0]
                    * unyt.g ** unitdict["U_M exponent"][0]
                    * unyt.K ** unitdict["U_T exponent"][0]
                    * unyt.s ** unitdict["U_t exponent"][0]
                )
                factor.convert_to_base("galactic")
                data *= factor
                return data
