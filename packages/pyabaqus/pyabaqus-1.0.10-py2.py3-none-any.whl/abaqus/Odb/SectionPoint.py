class SectionPoint:
    """The SectionPoint object describes the location of a section point within a section
    category. 

    Access
    ------
        - import
        - odbAccess
        - session.odbs[name].parts[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].parts[name].elementSets[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].parts[name].nodeSets[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].parts[name].surfaces[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.elementSets[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.instances[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.instances[name].elementSets[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.instances[name].nodeSets[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.instances[name].surfaces[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.nodeSets[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].rootAssembly.surfaces[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].sectionCategories[name].sectionPoints[i]
        - session.odbs[name].steps[name].frames[i].fieldOutputs[name].locations[i].sectionPoints[i]
        - session.odbs[name].steps[name].frames[i].fieldOutputs[name].values[i].instance.elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].steps[name].frames[i].fieldOutputs[name].values[i].instance.elementSets[name].elements[i].sectionCategory\
        - .sectionPoints[i]
        - session.odbs[name].steps[name].frames[i].fieldOutputs[name].values[i].instance.nodeSets[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].steps[name].frames[i].fieldOutputs[name].values[i].instance.surfaces[name].elements[i].sectionCategory.sectionPoints[i]
        - session.odbs[name].steps[name].frames[i].fieldOutputs[name].values[i].sectionPoint

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    def __init__(self, number: int, description: str):
        """This method creates a SectionPoint object.

        Path
        ----
            - session.odbs[*name*].sectionCategories[*name*].SectionPoint

        Parameters
        ----------
        number
            An Int specifying the number of the section point. See Beam elements and Shell elements 
            for the numbering convention. 
        description
            A String specifying the description of the section point. 

        Returns
        -------
            A SectionPoint object. . 
        """
        pass
