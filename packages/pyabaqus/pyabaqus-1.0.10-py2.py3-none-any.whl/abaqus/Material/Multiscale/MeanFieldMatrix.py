class MeanFieldMatrix:
    """The MeanFieldMatrix object specifies the matrix property.

    Access
    ------
        - import material
        - mdb.models[name].materials[name].constituents[name]
        - import odbMaterial
        - session.odbs[name].materials[name].constituents[name]

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------
        - CONSTITUENT

    """

    def __init__(self, name: str, material: str = '', isotropizationCoefficient: float = None):
        """This method creates a MeanFieldMatrix object.

        Path
        ----
            - mdb.models[name].materials[name].meanFieldHomogenization.MeanFieldMatrix
            - session.odbs[name].materials[name].meanFieldHomogenization.MeanFieldMatrix

        Parameters
        ----------
        name
            A String specifying the constituent repository key. 
        material
            A String specifying the name of the material. 
        isotropizationCoefficient
            A Float specifying the factor used for scaling the Plastic strain of the constituent
            when calculating the isotropic part of the tangent. 

        Returns
        -------
            A MeanFieldMatrix object. 

        Raises
        ------
            RangeError. 
        """
        pass

    def setValues(self):
        """This method modifies the MeanFieldMatrix object.

        Parameters
        ----------

        Returns
        -------
            None. 

        Raises
        ------
            RangeError. 
        """
        pass
