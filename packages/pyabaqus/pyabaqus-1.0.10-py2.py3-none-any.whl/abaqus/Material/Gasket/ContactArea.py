from abaqusConstants import *


class ContactArea:
    """A ContactArea object specifies a suboption of gasket thickness behavior when
    *variableUnits*=FORCE on the GasketThicknessBehavior object. The ContactArea object 
    defines the contact area or contact width versus closure curves to output an average 
    pressure through variable CS11. 

    Access
    ------
        - import material
        - mdb.models[name].materials[name].gasketThicknessBehavior.contactArea
        - import odbMaterial
        - session.odbs[name].materials[name].gasketThicknessBehavior.contactArea

    Table Data
    ----------
        - Contact area or width; this value must be positive.
        - Closure; this value must be positive.
        - Temperature, if the data depend on temperature.
        - Value of the first field variable, if the data depend on field variables.
        - Value of the second field variable.
        - Etc.

    Corresponding analysis keywords
    -------------------------------
        - GASKET CONTACT AREA

    """

    def __init__(self, table: tuple, temperatureDependency: Boolean = OFF, dependencies: int = 0):
        """This method creates a ContactArea object.

        Path
        ----
            - mdb.models[name].materials[name].gasketThicknessBehavior.ContactArea
            - session.odbs[name].materials[name].gasketThicknessBehavior.ContactArea

        Parameters
        ----------
        table
            A sequence of sequences of Floats specifying the items described below. 
        temperatureDependency
            A Boolean specifying whether contact area data depend on temperature. The default value 
            is OFF. 
        dependencies
            An Int specifying the number of field variable dependencies included in the definition 
            of the contact area data, in addition to temperature. The default value is 0. 

        Returns
        -------
            A ContactArea object. . 
        """
        pass

    def setValues(self):
        """This method modifies the ContactArea object.

        Parameters
        ----------
        """
        pass
