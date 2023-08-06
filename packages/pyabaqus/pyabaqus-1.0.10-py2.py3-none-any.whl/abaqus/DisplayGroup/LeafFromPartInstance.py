from abaqusConstants import *
from .Leaf import Leaf


class LeafFromPartInstance(Leaf):
    """The LeafFromPartInstance object can be used whenever a Leaf object is expected as an
    argument. Leaf objects are used to specify the items in a display group. Leaf objects 
    are constructed as temporary objects, which are then used as arguments to DisplayGroup 
    commands. 
    The LeafFromPartInstance object is derived from the Leaf object. 

    Access
    ------
        - import displayGroupOdbToolset

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # A SymbolicConstant specifying the leaf type. Possible values are EMPTY_LEAF, 
    # DEFAULT_MODEL, ALL_ELEMENTS, ALL_NODES, and ALL_SURFACES. 
    leafType: SymbolicConstant = None

    def __init__(self, partInstanceName: tuple):
        """This method creates a Leaf object from a list of part instance names.

        Path
        ----
            - LeafFromPartInstance

        Parameters
        ----------
        partInstanceName
            A sequence of Strings specifying the names of the part instances. 

        Returns
        -------
            A LeafFromPartInstance object. . 
        """
        super().__init__(DEFAULT_MODEL)
        pass
