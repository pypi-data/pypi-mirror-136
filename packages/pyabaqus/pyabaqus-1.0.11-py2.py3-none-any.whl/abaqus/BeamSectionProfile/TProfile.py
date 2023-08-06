from .Profile import Profile

class TProfile(Profile):

    """The TProfile object defines the properties of a T profile. 
    The TProfile object is derived from the Profile object. 

    Access
    ------
        - import section
        - mdb.models[name].profiles[name]
        - import odbSection
        - session.odbs[name].profiles[name]

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------
        - BEAM SECTION

    """

    def __init__(self, name: str, b: float, h: float, l: float, tf: float, tw: float):
        """This method creates a TProfile object.

        Path
        ----
            - mdb.models[name].TProfile
            - session.odbs[name].TProfile

        Parameters
        ----------
        name
            A String specifying the repository key. 
        b
            A positive Float specifying the *b* dimension (flange width) of the T profile. For more 
            information, see [Beam cross-section 
            library](https://help.3ds.com/2021/English/DSSIMULIA_Established/SIMACAEELMRefMap/simaelm-c-beamcrosssectlib.htm?ContextScope=all). 
        h
            A positive Float specifying the *h* dimension (height) of the T profile. 
        l
            A positive Float specifying the *l* dimension (offset of 1–axis from the edge of web) of 
            the T profile. 
        tf
            A positive Float specifying the *tf* dimension (flange thickness) of the T profile (*tf 
            < h*). 
        tw
            A positive Float specifying the *tw* dimension (web thickness) of the T profile (*tw< 
            b*). 

        Returns
        -------
            A TProfile object. 

        Raises
        ------
            RangeError. 
            !img 
        """
        super().__init__()
        pass

    def setValues(self):
        """This method modifies the TProfile object.

        Parameters
        ----------

        Returns
        -------
            None. 

        Raises
        ------
            RangeError. 
            !img 
        """
        pass

