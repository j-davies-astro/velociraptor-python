"""
Autoplotter module. Contains the functionality to use the library
to automatically make plots of variable x against variable y, by
reading from a yaml file.

This yaml file has the following format:

output_filename: 
    params:
        type: scatter / histogram / 2dhistogram / massfunction
        number_of_bins: 128
        #TODO:
        norm: log
    x:
        quantity: "quantity.name"
        units: Solar_Mass
        log: true
        label_override: "string"
        # if hist or massfunc, in units
        start_bin: 0
        end_bin: 1e10
    y:  quantity: "quantity.name"
        units: Solar_Mass
        log: true
        label_override: "string"
        # if hist
        start_bin: 0
        end_bin: 1e10
    median:
        plot: true
        log: true
        number_of_bins: 10
        start:
            value: 1e10
            units: Solar_Mass
        end:
            value: 1e12
            units: Solar_Mass
    mean:
        plot: false
        log: true
        number_of_bins: 10
        start:
            value: 1e10
            units: Solar_Mass
        end:
            value: 1e12
            units: Solar_Mass
"""
