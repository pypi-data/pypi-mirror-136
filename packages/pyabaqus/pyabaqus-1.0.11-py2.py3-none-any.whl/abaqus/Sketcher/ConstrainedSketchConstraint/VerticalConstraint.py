from .ConstrainedSketchConstraint import ConstrainedSketchConstraint
from ..ConstrainedSketchGeometry.ConstrainedSketchGeometry import ConstrainedSketchGeometry


class VerticalConstraint(ConstrainedSketchConstraint):

    def __init__(self, entity: ConstrainedSketchGeometry):
        """This method creates a vertical constraint. This constraint applies to a line and
        constrains it to be vertical.

        Path
        ----
            - mdb.models[name].sketches[name].VerticalConstraint

        Parameters
        ----------
        entity
            A ConstrainedSketchGeometry object specifying the line to constrain. 

        Returns
        -------
            A ConstrainedSketchConstraint object. . 
            !img 
        """
        pass
