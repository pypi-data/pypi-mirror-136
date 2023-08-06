from abaqusConstants import *


class OdbDiagnosticAttempt:
    """The OdbDiagnosticAttempt object.

    Access
    ------
        - import visualization
        - session.odbData[name].diagnosticData.steps[i].increments[i].attempts[i]

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # A boolean specifying the state of Auto-stablilization. This attribute is read-only. 
    autoStabilize: Boolean = OFF

    # A boolean specifying the state of convergence for the attempt. This attribute is 
    # read-only. 
    isConverged: Boolean = OFF

    # A boolean specifying the state of cutback. This attribute is read-only. 
    isCutBack: Boolean = OFF

    # A boolean specifying whether or not reordering is needed. This attribute is read-only. 
    needsReordering: Boolean = OFF

    # An int specifying the number of cutback diagnostics. This attribute is read-only. 
    numberOfCutbackDiagnostics: str = ''

    # An int specifying the number of iterations for the particular attempt. This attribute is 
    # read-only. 
    numberOfIterations: str = ''

    # An int specifying the number of iterations with severe discontinuities This attribute is 
    # read-only. 
    numberOfSevereDiscontinuityIterations: str = ''

    # A float specifying the size of the increment of the particular attempt. This attribute 
    # is read-only. 
    size: str = ''
