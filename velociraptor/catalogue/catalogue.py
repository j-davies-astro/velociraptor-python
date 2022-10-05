"""
Main objects for the velociraptor reading library.

This is based upon the reading routines in the SWIFTsimIO library.
"""

from typing import Union, List, Callable


class Catalogue:

    # top level definitions for autocomplete
    registration_functions: Union[List[Callable], None]
