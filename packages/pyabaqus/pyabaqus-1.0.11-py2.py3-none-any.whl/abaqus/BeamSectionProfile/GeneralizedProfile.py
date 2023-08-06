from .Profile import Profile

class GeneralizedProfile(Profile):

    """The GeneralizedProfile object defines the properties of a profile via its area, moment 
    of inertia, etc. 
    The GeneralizedProfile object is derived from the Profile object. 

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
        - BEAM GENERAL SECTION

    """

    def __init__(self, name: str, area: float, i11: float, i12: float, i22: float, j: float, gammaO: float, 
                 gammaW: float):
        """This method creates a GeneralizedProfile object.

        Path
        ----
            - mdb.models[name].GeneralizedProfile
            - session.odbs[name].GeneralizedProfile

        Parameters
        ----------
        name
            A String specifying the repository key. 
        area
            A Float specifying the cross-sectional area for the profile. 
        i11
            A Float specifying the moment of inertia for bending about the 1-axis, I11I11. 
        i12
            A Float specifying the moment of inertia for cross bending, I12I12. 
        i22
            A Float specifying the moment of inertia for bending about the 2-axis, I22I22. 
        j
            A Float specifying the torsional constant, JJ. 
        gammaO
            A Float specifying the sectorial moment, Γ0Γ0. 
        gammaW
            A Float specifying the warping constant, ΓWΓW. 

        Returns
        -------
            A GeneralizedProfile object. 

        Raises
        ------
            RangeError. 
            !img 
        """
        super().__init__()
        pass

    def setValues(self):
        """This method modifies the GeneralizedProfile object.

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

