from .Material import Material
from ..Odb.OdbBase import OdbBase


class MaterialOdb(OdbBase):

    def Material(self, name: str, description: str = '', materialIdentifier: str = ''):
        """This method creates a Material object.

        Path
        ----
            - session.odbs[name].Material

        Parameters
        ----------
        name
            A String specifying the name of the new material.
        description
            A String specifying user description of the material. The default value is an empty
            string.
        materialIdentifier
            A String specifying material identifier for customer use. The default value is an empty
            string.

        Returns
        -------
            A Material object..
        """
        self.materials[name] = material = Material(name, description, materialIdentifier)
        return material
