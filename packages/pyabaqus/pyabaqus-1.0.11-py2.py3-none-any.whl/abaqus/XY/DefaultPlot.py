from .Area import Area
from .Title import Title


class DefaultPlot:
    """The DefaultPlot object is used to hold on default plot attributes. The DefaultPlot
    object attributes are used whenever an XYPlot object is created. A DefaultPlot object is 
    automatically created when opening a session. 

    Access
    ------
        - import visualization
        - session.defaultPlot

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # An Area object specifying an Area used to hold on to the default display properties for 
    # the plot area. 
    area: Area = Area()

    # A Title object specifying a Title object used to hold on to the default properties of 
    # the XY-Plot title. 
    title: Title = Title()
