from abaqusConstants import *


class Fastener:
    """The Fastener object is the abstract base type for PointFastener, DiscreteFastener, and
    AssembledFastener. 

    Access
    ------
        - import part
        - mdb.models[name].parts[name].engineeringFeatures.fasteners[name]
        - import assembly
        - mdb.models[name].rootAssembly.engineeringFeatures.fasteners[name]

    Table Data
    ----------

    Corresponding analysis keywords
    -------------------------------

    """

    # A String specifying the repository key. 
    name: str = ''

    # A Boolean specifying whether the fastener is suppressed or not. The default value is 
    # OFF. 
    suppressed: Boolean = OFF

    def resume(self):
        """This method resumes the fastener that was previously suppressed.

        Parameters
        ----------
        """
        pass

    def suppress(self):
        """This method suppresses the fastener.

        Parameters
        ----------
        """
        pass
