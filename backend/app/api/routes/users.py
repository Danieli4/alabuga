"""Маршруты работы с профилем."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rank import Rank
from app.models.user import User, UserRole, UserCompetency
from app.models.mission import SubmissionStatus
from app.schemas.progress import ProgressSnapshot
from app.schemas.rank import RankBase
from app.schemas.user import LeaderboardEntry, UserCompetencyRead, UserProfile
from app.services.rank import build_progress_snapshot

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/me", response_model=UserProfile, summary="Профиль пилота")
def get_profile(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> UserProfile:
    """Возвращаем профиль и связанные сущности."""

    db.refresh(current_user)
    for item in current_user.competencies:
        _ = item.competency
    for artifact in current_user.artifacts:
        _ = artifact.artifact
    return UserProfile.model_validate(current_user)


@router.get("/ranks", response_model=list[RankBase], summary="Перечень рангов")
def list_ranks(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[RankBase]:
    """Возвращаем ранги по возрастанию требований."""

    ranks = db.query(Rank).order_by(Rank.required_xp).all()
    return [RankBase.model_validate(rank) for rank in ranks]


@router.get("/progress", response_model=ProgressSnapshot, summary="Прогресс до следующего ранга")
def get_progress(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ProgressSnapshot:
    """Возвращаем агрегированную информацию о выполненных условиях следующего ранга."""

    db.refresh(current_user)
    _ = current_user.submissions
    _ = current_user.competencies
    snapshot = build_progress_snapshot(current_user, db)
    return snapshot


@router.get("/leaderboard", response_model=list[LeaderboardEntry], summary="Лидерборд пилотов")
def leaderboard(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[LeaderboardEntry]:
    """Возвращаем пилотов, отсортированных по опыту с перечислением компетенций."""

    users = (
        db.query(User)
        .filter(User.role == UserRole.PILOT)
        .options(
            selectinload(User.current_rank),
            selectinload(User.competencies).selectinload(UserCompetency.competency),
            selectinload(User.submissions),
        )
        .order_by(User.xp.desc(), User.created_at)
        .all()
    )

    leaderboard: list[LeaderboardEntry] = []
    for user in users:
        completed = sum(1 for submission in user.submissions if submission.status == SubmissionStatus.APPROVED)
        competencies = [UserCompetencyRead.model_validate(entry) for entry in user.competencies]
        leaderboard.append(
            LeaderboardEntry(
                user_id=user.id,
                full_name=user.full_name,
                rank_title=user.current_rank.title if user.current_rank else None,
                xp=user.xp,
                mana=user.mana,
                completed_missions=completed,
                competencies=competencies,
            )
        )

    return leaderboard
