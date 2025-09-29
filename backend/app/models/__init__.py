"""Инициализация моделей для удобных импортов."""

from .artifact import Artifact  # noqa: F401
from .branch import Branch, BranchMission  # noqa: F401
from .journal import JournalEntry  # noqa: F401
from .mission import Mission, MissionCompetencyReward, MissionPrerequisite, MissionSubmission  # noqa: F401
from .coding import CodingAttempt, CodingChallenge  # noqa: F401
from .onboarding import OnboardingSlide, OnboardingState  # noqa: F401
from .python import PythonChallenge, PythonSubmission, PythonUserProgress  # noqa: F401
from .rank import Rank, RankCompetencyRequirement, RankMissionRequirement  # noqa: F401
from .store import Order, StoreItem  # noqa: F401
from .user import Competency, User, UserArtifact, UserCompetency  # noqa: F401

__all__ = [
    "Artifact",
    "Branch",
    "BranchMission",
    "JournalEntry",
    "CodingChallenge",
    "CodingAttempt",
    "Mission",
    "MissionCompetencyReward",
    "MissionPrerequisite",
    "MissionSubmission",
    "OnboardingSlide",
    "OnboardingState",
    "PythonChallenge",
    "PythonSubmission",
    "PythonUserProgress",
    "Rank",
    "RankCompetencyRequirement",
    "RankMissionRequirement",
    "Order",
    "StoreItem",
    "Competency",
    "User",
    "UserArtifact",
    "UserCompetency",
]
