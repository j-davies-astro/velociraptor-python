import h5py
import os
import unyt


class VelociraptorCatalogueReader:
    def __init__(self, filename):
        with h5py.File(filename, "r") as handle:
            if ("Parameters" in handle) and (
                "vr_basename" in handle["Parameters"].attrs
            ):
                self.type = "new"
            else:
                self.type = "old"

            self.filename = filename

    def get_name(self):
        return self.filename

    def is_old_catalogue(self):
        return self.type == "old"

    def get_cosmology(self):
        assert self.type == "new"
        with h5py.File(self.filename, "r") as handle:
            cosmo = handle["SWIFT/Cosmology"].attrs
            a = cosmo["Scale-factor"][0]
            z = cosmo["Redshift"][0]
        return a, z

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
