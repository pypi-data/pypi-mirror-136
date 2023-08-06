class ResponseSpectrumComponent:
    """A ResponseSpectrumComponent is an element of the ResponseSpectrumComponentArray.

    Access
    ------
        - import step
        - mdb.models[name].steps[name].components[i]

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # A Float specifying the *X*-direction cosine. 
    x: float = None

    # A Float specifying the *Y*-direction cosine. 
    y: float = None

    # A Float specifying the *Z*-direction cosine. 
    z: float = None

    # A Float specifying the scale factor. 
    scale: float = None

    # A Float specifying the time duration of the dynamic event, from which this spectrum was 
    # created.Note:This parameter is ignored unless used with the DSC modal summation rule. 
    timeDuration: float = None

    # A String specifying the name of the response spectrum specified with the keyword 
    # SPECTRUM. 
    respSpectrum: str = ''
