from velociraptor.objects import VelociraptorCatalogue


def load(filename):
    """
    Loads a velociraptor catalogue, producing a VelociraptorCatalogue
    object.
    """

    return VelociraptorCatalogue(filename)
