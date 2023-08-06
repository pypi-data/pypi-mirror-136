class TieConstraint:
    """The TieConstraint object.

    Access
    ------
        - import visualization
        - session.odbData[name].ties[i]

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # A String specifying the tie constraint name. This attribute is read-only. 
    name: str = ''

    def constraintData(self):
        """This method returns constraint data if any are associated with the object

        Parameters
        ----------

        Returns
        -------
            A tuple containing coordinates of the nodes pertaining to the constraint. . 
        """
        pass
