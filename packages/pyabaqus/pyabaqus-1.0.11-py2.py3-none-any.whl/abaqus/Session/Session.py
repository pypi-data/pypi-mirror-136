from ..Animation.AnimationSession import AnimationSession
from ..DisplayGroup.DisplayGroupSession import DisplayGroupSession
from ..FieldReport.FieldReportSession import FieldReportSession
from ..Job.JobSession import JobSession
from ..Odb.OdbSession import OdbSession
from ..PathAndProbe.PathSession import PathSession
from ..XY.XYSession import XYSession


class Session(AnimationSession, DisplayGroupSession, FieldReportSession, JobSession, OdbSession, PathSession, XYSession):
    pass
