from abaqusConstants import *
from abaqus.Material.Ratios import Ratios


class Swelling:
    """The Swelling object specifies time-dependent volumetric swelling for a material.

    Access
    ------
        - import material
        - mdb.models[name].materials[name].swelling
        - import odbMaterial
        - session.odbs[name].materials[name].swelling

    Table Data
    ----------
        - Volumetric swelling strain rate.
        - Temperature, if the data depend on temperature.
        - Value of the first field variable, if the data depend on field variables.
        - Value of the second field variable.
        - Etc.

    Corresponding analysis keywords
    -------------------------------
        - SWELLING

    """

    # A Ratios object. 
    ratios: Ratios = Ratios(((),))

    def __init__(self, table: tuple, law: SymbolicConstant = INPUT, temperatureDependency: Boolean = OFF,
                 dependencies: int = 0):
        """This method creates a Swelling object.

        Path
        ----
            - mdb.models[name].materials[name].Swelling
            - session.odbs[name].materials[name].Swelling

        Parameters
        ----------
        table
            A sequence of sequences of Floats specifying the items described below.This argument is 
            valid only when *law*=INPUT. 
        law
            A SymbolicConstant specifying the type of data defining the swelling behavior. Possible 
            values are INPUT and USER. The default value is INPUT. 
        temperatureDependency
            A Boolean specifying whether the data depend on temperature. The default value is OFF. 
        dependencies
            An Int specifying the number of field variable dependencies. The default value is 0. 

        Returns
        -------
            A Swelling object. 

        Raises
        ------
            RangeError. 
        """
        pass

    def setValues(self):
        """This method modifies the Swelling object.

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
