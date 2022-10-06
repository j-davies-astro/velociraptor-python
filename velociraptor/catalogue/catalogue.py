"""
Main objects for the velociraptor reading library.

This is based upon the reading routines in the SWIFTsimIO library.
"""

from typing import Union, List, Callable

from velociraptor.catalogue.derived import DerivedQuantities

from functools import reduce


class Catalogue:

    # top level definitions for autocomplete
    registration_functions: Union[List[Callable], None]

    def get_quantity(self, quantity_name: str):
        """
        Get a quantity from the catalogue.

        Parameters
        ----------

        quantity_name: str
            Full path to the quantity.
        """
        return reduce(getattr, quantity_name.split("."), self)

    def register_derived_quantities(
        self, registration_file_path: Union[List[str], str]
    ) -> None:
        """
        Register any required derived quantities. These will
        be available through `catalogue.derived_quantities.{your_names}`.

        For more information on this feature, see the documentation of
        :class:`velociraptor.catalogue.derived.DerivedQuantities`.

        Parameters
        ----------

        registration_file_path: Union[List[str], str]
            Path to the python source file(s) that contain(s) the code to
            register the additional derived quantities.
        """

        self.derived_quantities = DerivedQuantities(registration_file_path, self)

        return
