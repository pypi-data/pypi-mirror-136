from abaqus.Material.Ratios import Ratios


class MoistureSwelling:
    """The MoistureSwelling object defines moisture-driven swelling.

    Access
    ------
        - import material
        - mdb.models[name].materials[name].moistureSwelling
        - import odbMaterial
        - session.odbs[name].materials[name].moistureSwelling

    Table Data
    ----------
        - Volumetric moisture swelling strain, εm⁢s.
        - Saturation, s. This value must lie in the range 0≤s≤1.0.

    Corresponding analysis keywords
    -------------------------------
        - MOISTURE SWELLING

    """

    # A Ratios object. 
    ratios: Ratios = Ratios(((),))

    def __init__(self, table: tuple):
        """This method creates a MoistureSwelling object.

        Path
        ----
            - mdb.models[name].materials[name].MoistureSwelling
            - session.odbs[name].materials[name].MoistureSwelling

        Parameters
        ----------
        table
            A sequence of sequences of Floats specifying the items described below. 

        Returns
        -------
            A MoistureSwelling object. . 
        """
        pass

    def setValues(self):
        """This method modifies the MoistureSwelling object.

        Parameters
        ----------
        """
        pass
