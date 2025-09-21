"""HR-панель и административные действия."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_hr
from app.db.session import get_db
from app.models.branch import BranchMission
from app.models.mission import Mission, MissionCompetencyReward, MissionPrerequisite, MissionSubmission, SubmissionStatus
from app.models.rank import Rank
from app.schemas.mission import MissionBase, MissionCreate, MissionDetail, MissionSubmissionRead
from app.schemas.rank import RankBase
from app.services.mission import approve_submission, reject_submission

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/missions", response_model=list[MissionBase], summary="Миссии (HR)")
def admin_missions(*, db: Session = Depends(get_db), current_user=Depends(require_hr)) -> list[MissionBase]:
    """Список всех миссий для HR."""

    missions = db.query(Mission).order_by(Mission.title).all()
    return [MissionBase.model_validate(mission) for mission in missions]


@router.post("/missions", response_model=MissionDetail, summary="Создать миссию")
def create_mission_endpoint(
    mission_in: MissionCreate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> MissionDetail:
    """Создаём новую миссию."""

    mission = Mission(
        title=mission_in.title,
        description=mission_in.description,
        xp_reward=mission_in.xp_reward,
        mana_reward=mission_in.mana_reward,
        difficulty=mission_in.difficulty,
        minimum_rank_id=mission_in.minimum_rank_id,
        artifact_id=mission_in.artifact_id,
    )
    db.add(mission)
    db.flush()

    for reward in mission_in.competency_rewards:
        db.add(
            MissionCompetencyReward(
                mission_id=mission.id,
                competency_id=reward.competency_id,
                level_delta=reward.level_delta,
            )
        )

    for prerequisite_id in mission_in.prerequisite_ids:
        db.add(
            MissionPrerequisite(mission_id=mission.id, required_mission_id=prerequisite_id)
        )

    if mission_in.branch_id:
        db.add(
            BranchMission(
                branch_id=mission_in.branch_id,
                mission_id=mission.id,
                order=mission_in.branch_order,
            )
        )

    db.commit()
    db.refresh(mission)

    return MissionDetail(
        id=mission.id,
        title=mission.title,
        description=mission.description,
        xp_reward=mission.xp_reward,
        mana_reward=mission.mana_reward,
        difficulty=mission.difficulty,
        is_active=mission.is_active,
        minimum_rank_id=mission.minimum_rank_id,
        artifact_id=mission.artifact_id,
        prerequisites=[link.required_mission_id for link in mission.prerequisites],
        competency_rewards=[
            {
                "competency_id": reward.competency_id,
                "competency_name": reward.competency.name,
                "level_delta": reward.level_delta,
            }
            for reward in mission.competency_rewards
        ],
        created_at=mission.created_at,
        updated_at=mission.updated_at,
    )


@router.get("/ranks", response_model=list[RankBase], summary="Список рангов")
def admin_ranks(*, db: Session = Depends(get_db), current_user=Depends(require_hr)) -> list[RankBase]:
    """Перечень рангов."""

    ranks = db.query(Rank).order_by(Rank.required_xp).all()
    return [RankBase.model_validate(rank) for rank in ranks]


@router.get(
    "/submissions",
    response_model=list[MissionSubmissionRead],
    summary="Очередь модерации",
)
def moderation_queue(
    status_filter: SubmissionStatus = SubmissionStatus.PENDING,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> list[MissionSubmissionRead]:
    """Возвращаем отправки со статусом по умолчанию pending."""

    submissions = (
        db.query(MissionSubmission)
        .filter(MissionSubmission.status == status_filter)
        .order_by(MissionSubmission.created_at)
        .all()
    )
    return [MissionSubmissionRead.model_validate(submission) for submission in submissions]


@router.post(
    "/submissions/{submission_id}/approve",
    response_model=MissionSubmissionRead,
    summary="Одобрить миссию",
)
def approve_submission_endpoint(
    submission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> MissionSubmissionRead:
    """HR подтверждает выполнение."""

    submission = db.query(MissionSubmission).filter(MissionSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отправка не найдена")
    submission = approve_submission(db, submission)
    return MissionSubmissionRead.model_validate(submission)


@router.post(
    "/submissions/{submission_id}/reject",
    response_model=MissionSubmissionRead,
    summary="Отклонить миссию",
)
def reject_submission_endpoint(
    submission_id: int,
    comment: str | None = None,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> MissionSubmissionRead:
    """HR отклоняет выполнение."""

    submission = db.query(MissionSubmission).filter(MissionSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отправка не найдена")
    submission = reject_submission(db, submission, comment)
    return MissionSubmissionRead.model_validate(submission)
