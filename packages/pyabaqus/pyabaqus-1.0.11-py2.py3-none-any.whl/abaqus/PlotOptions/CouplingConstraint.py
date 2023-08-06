class CouplingConstraint:
    """The CouplingConstraint object.

    Access
    ------
        - import visualization
        - session.odbData[name].kinematicCouplings[i]
        - session.odbData[name].distributingCouplings[i]
        - session.odbData[name].shellSolidCouplings[i]

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # A String specifying the coupling name. This attribute is read-only. 
    name: str = ''

    # A String specifying the type of coupling. This attribute is read-only. 
    type: str = ''

    def constraintData(self):
        """This method returns node numbers of the surface being controlled by the control point.

        Parameters
        ----------

        Returns
        -------
            Tuple-of-Ints Dictionary specifying the node numbers on the controlled surface. . 
        """
        pass
