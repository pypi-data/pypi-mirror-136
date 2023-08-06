from abaqusConstants import *


class DeformationPlasticity:
    """The DeformationPlasticity object specifies the deformation plasticity model.

    Access
    ------
        - import material
        - mdb.models[name].materials[name].deformationPlasticity
        - import odbMaterial
        - session.odbs[name].materials[name].deformationPlasticity

    Table Data
    ----------
        - Young's modulus, E.
        - Poisson's ratio, ν.
        - Yield stress, σ0.
        - Exponent, n.
        - Yield offset, α.
        - Temperature, if the data depend on temperature.

    Corresponding analysis keywords
    -------------------------------
        - DEFORMATION PLASTICITY

    """

    def __init__(self, table: tuple, temperatureDependency: Boolean = OFF):
        """This method creates a DeformationPlasticity object.

        Path
        ----
            - mdb.models[name].materials[name].DeformationPlasticity
            - session.odbs[name].materials[name].DeformationPlasticity

        Parameters
        ----------
        table
            A sequence of sequences of Floats specifying the items described below. 
        temperatureDependency
            A Boolean specifying whether the data depend on temperature. The default value is OFF. 

        Returns
        -------
            A DeformationPlasticity object. 

        Raises
        ------
            RangeError. 
        """
        pass

    def setValues(self):
        """This method modifies the DeformationPlasticity object.

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
