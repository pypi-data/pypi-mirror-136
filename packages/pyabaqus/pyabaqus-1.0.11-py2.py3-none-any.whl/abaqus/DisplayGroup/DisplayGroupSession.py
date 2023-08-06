from .DisplayGroup import DisplayGroup
from .Leaf import Leaf
from ..Session.SessionBase import SessionBase


class DisplayGroupSession(SessionBase):

    def DisplayGroup(self, name: str, leaf: Leaf) -> DisplayGroup:
        """This method creates a DisplayGroup object.

        Path
        ----
            - session.DisplayGroup

        Parameters
        ----------
        name
            A String specifying the repository key.
        leaf
            A Leaf object specifying the items in the display group.

        Returns
        -------
            A DisplayGroup object..
        """
        self.displayGroups[name] = displayGroup = DisplayGroup(name, leaf)
        return displayGroup
