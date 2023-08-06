from ..Adaptivity.AdaptivityModel import AdaptivityModel
from ..Amplitude.AmplitudeModel import AmplitudeModel
from ..Assembly.AssemblyModel import AssemblyModel
from ..BeamSectionProfile.BeamSectionProfileModel import BeamSectionProfileModel
from ..BoundaryCondition.BoundaryConditionModel import BoundaryConditionModel
from ..Calibration.CalibrationModel import CalibrationModel
from ..Constraint.ConstraintModel import ConstraintModel
from ..Filter.FilterModel import FilterModel
from ..Interaction.InteractionModel import InteractionModel
from ..LoadAndLoadCase.LoadModel import LoadModel
from ..Material.MaterialModel import MaterialModel
from ..Optimization.OptimizationTaskModel import OptimizationTaskModel
from ..Part.PartModel import PartModel
from ..PredefinedField.PredefinedFieldModel import PredefinedFieldModel
from ..Section.SectionModel import SectionModel
from ..Sketcher.SketchModel import SketchModel
from ..Step.StepModel import StepModel
from ..StepOutput.OutputModel import OutputModel
from ..TableCollection.TableCollectionModel import TableCollectionModel


class Model(AdaptivityModel, AssemblyModel, AmplitudeModel, BoundaryConditionModel, CalibrationModel, ConstraintModel,
            FilterModel, InteractionModel, LoadModel, MaterialModel, OptimizationTaskModel, PartModel,
            PredefinedFieldModel, BeamSectionProfileModel, OutputModel, SectionModel, SketchModel, StepModel,
            TableCollectionModel):
    pass
