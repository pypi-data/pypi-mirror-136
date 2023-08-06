from .ConstrainedSketchConstraint import ConstrainedSketchConstraint
from ..ConstrainedSketchGeometry.ConstrainedSketchGeometry import ConstrainedSketchGeometry


class PerpendicularConstraint(ConstrainedSketchConstraint):

    def __init__(self, entity1: ConstrainedSketchGeometry, entity2: ConstrainedSketchGeometry):
        """This method creates a perpendicular constraint. This constraint applies to different
        types of ConstrainedSketchGeometry objects and constrains them to be perpendicular to
        each other.

        Path
        ----
            - mdb.models[name].sketches[name].PerpendicularConstraint

        Parameters
        ----------
        entity1
            A ConstrainedSketchGeometry object specifying the first object. 
        entity2
            A ConstrainedSketchGeometry object specifying the second object. 

        Returns
        -------
            A ConstrainedSketchConstraint object. . 
            !img 
        """
        pass
