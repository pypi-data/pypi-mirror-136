from abaqusConstants import *


class JobData:
    """The JobData object describes the context in which the analysis was run.

    Access
    ------
        - import odbAccess
        - session.odbs[name].jobData

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # A String specifying the name of the job. 
    name: str = ''

    # A SymbolicConstant specifying the analysis code. Possible values are ABAQUS_STANDARD, 
    # ABAQUS_EXPLICIT, and UNKNOWN_ANALYSIS_CODE. 
    analysisCode: SymbolicConstant = None

    # A SymbolicConstant specifying the precision. Only SINGLE_PRECISION is currently 
    # supported. Possible values are DOUBLE_PRECISION and SINGLE_PRECISION. 
    precision: SymbolicConstant = None

    # A String specifying the release of the analysis code. 
    version: str = ''

    # A String specifying the date and time at which the analysis was run. 
    creationTime: str = ''

    # A String specifying the date and time at which the database was last modified. 
    modificationTime: str = ''

    # A String specifying the name of the machine on which the analysis was run. 
    machineName: str = ''

    # A String specifying an odb_Sequence of productAddOns. Possible values are: Possible 
    # values are AQUA, DESIGN, BIORID, CEL, SOLITER, and CAVPARALLEL. 
    productAddOns: str = ''
