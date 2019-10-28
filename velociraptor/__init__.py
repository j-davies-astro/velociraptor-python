from velociraptor.catalogue import generate_catalogue


def load(filename):
    """
    Loads a velociraptor catalogue, producing a VelociraptorCatalogue
    object.
    """

    return generate_catalogue(filename)
