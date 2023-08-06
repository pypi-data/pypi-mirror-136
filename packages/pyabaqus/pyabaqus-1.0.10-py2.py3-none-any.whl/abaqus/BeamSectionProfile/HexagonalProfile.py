from .Profile import Profile

class HexagonalProfile(Profile):

    """The HexagonalProfile object defines the properties of a hexagonal profile. 
    The HexagonalProfile object is derived from the Profile object. 

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

    def __init__(self, name: str, r: float, t: float):
        """This method creates a HexagonalProfile object.

        Path
        ----
            - mdb.models[name].HexagonalProfile
            - session.odbs[name].HexagonalProfile

        Parameters
        ----------
        name
            A String specifying the repository key. 
        r
            A positive Float specifying the *r* dimension (outer radius) of the hexagonal profile. 
            For more information, see [Beam cross-section 
            library](https://help.3ds.com/2021/English/DSSIMULIA_Established/SIMACAEELMRefMap/simaelm-c-beamcrosssectlib.htm?ContextScope=all). 
        t
            A positive Float specifying the *t* dimension (wall thickness) of the hexagonal profile, 
            *t < (sqrt(3)/2)r*. 

        Returns
        -------
            A HexagonalProfile object. 

        Raises
        ------
            RangeError. 
            !img 
        """
        super().__init__()
        pass

    def setValues(self):
        """This method modifies the HexagonalProfile object.

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

