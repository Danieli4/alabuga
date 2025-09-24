"""Маршруты для работы с миссиями."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.branch import Branch, BranchMission
from app.models.mission import Mission, MissionSubmission
from app.models.user import User
from app.schemas.branch import BranchMissionRead, BranchRead
from app.schemas.mission import (
    MissionBase,
    MissionDetail,
    MissionSubmissionCreate,
    MissionSubmissionRead,
)
from app.services.mission import submit_mission

router = APIRouter(prefix="/api/missions", tags=["missions"])


@router.get("/branches", response_model=list[BranchRead], summary="Список веток миссий")
def list_branches(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[BranchRead]:
    """Возвращаем ветки с упорядоченными миссиями."""

    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions).selectinload(BranchMission.mission))
        .order_by(Branch.title)
        .all()
    )

    return [
        BranchRead(
            id=branch.id,
            title=branch.title,
            description=branch.description,
            category=branch.category,
            missions=[
                BranchMissionRead(
                    mission_id=item.mission_id,
                    mission_title=item.mission.title if item.mission else "",
                    order=item.order,
                )
                for item in sorted(branch.missions, key=lambda link: link.order)
            ],
        )
        for branch in branches
    ]


@router.get("/", response_model=list[MissionBase], summary="Список миссий")
def list_missions(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[MissionBase]:
    """Возвращаем доступные миссии."""

    query = db.query(Mission).filter(Mission.is_active.is_(True))
    if current_user.current_rank_id:
        query = query.filter(
            (Mission.minimum_rank_id.is_(None)) | (Mission.minimum_rank_id <= current_user.current_rank_id)
        )
    missions = query.all()
    return [MissionBase.model_validate(mission) for mission in missions]


@router.get("/{mission_id}", response_model=MissionDetail, summary="Карточка миссии")
def get_mission(
    mission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MissionDetail:
    """Возвращаем подробную информацию о миссии."""

    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.is_active.is_(True)).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")

    prerequisites = [link.required_mission_id for link in mission.prerequisites]
    rewards = [
        {
            "competency_id": reward.competency_id,
            "competency_name": reward.competency.name,
            "level_delta": reward.level_delta,
        }
        for reward in mission.competency_rewards
    ]

    data = MissionDetail(
        id=mission.id,
        title=mission.title,
        description=mission.description,
        xp_reward=mission.xp_reward,
        mana_reward=mission.mana_reward,
        difficulty=mission.difficulty,
        is_active=mission.is_active,
        minimum_rank_id=mission.minimum_rank_id,
        artifact_id=mission.artifact_id,
        prerequisites=prerequisites,
        competency_rewards=rewards,
        created_at=mission.created_at,
        updated_at=mission.updated_at,
    )
    return data


@router.post("/{mission_id}/submit", response_model=MissionSubmissionRead, summary="Отправляем отчёт")
def submit(
    mission_id: int,
    submission_in: MissionSubmissionCreate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MissionSubmissionRead:
    """Пилот отправляет доказательство выполнения миссии."""

    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")
    submission = submit_mission(
        db=db,
        user=current_user,
        mission=mission,
        comment=submission_in.comment,
        proof_url=submission_in.proof_url,
    )
    return MissionSubmissionRead.model_validate(submission)


@router.get(
    "/{mission_id}/submission",
    response_model=MissionSubmissionRead | None,
    summary="Получаем текущую отправку",
)
def get_submission(
    mission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MissionSubmissionRead | None:
    """Возвращаем статус отправленной миссии."""

    submission = (
        db.query(MissionSubmission)
        .filter(MissionSubmission.user_id == current_user.id, MissionSubmission.mission_id == mission_id)
        .first()
    )
    if not submission:
        return None
    return MissionSubmissionRead.model_validate(submission)
