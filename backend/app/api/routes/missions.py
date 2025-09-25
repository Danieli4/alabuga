"""Маршруты для работы с миссиями."""

from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.branch import Branch, BranchMission
from app.models.mission import Mission, MissionSubmission, SubmissionStatus
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


def _load_user_progress(user: User) -> set[int]:
    """Возвращаем идентификаторы успешно завершённых миссий."""

    completed = {
        submission.mission_id
        for submission in user.submissions
        if submission.status == SubmissionStatus.APPROVED
    }
    return completed


def _build_branch_dependencies(branches: list[Branch]) -> dict[int, set[int]]:
    """Строим карту зависимостей миссий по веткам."""

    dependencies: dict[int, set[int]] = defaultdict(set)
    for branch in branches:
        ordered = sorted(branch.missions, key=lambda item: item.order)
        previous: list[int] = []
        for link in ordered:
            if previous:
                dependencies[link.mission_id].update(previous)
            previous.append(link.mission_id)
    return dependencies


def _mission_availability(
    *,
    mission: Mission,
    user: User,
    completed_missions: set[int],
    branch_dependencies: dict[int, set[int]],
    mission_titles: dict[int, str],
) -> tuple[bool, list[str]]:
    """Определяем, доступна ли миссия и формируем причины блокировки."""

    reasons: list[str] = []

    if mission.minimum_rank and user.xp < mission.minimum_rank.required_xp:
        reasons.append(f"Требуется ранг «{mission.minimum_rank.title}»")

    missing_explicit = [
        req.required_mission_id
        for req in mission.prerequisites
        if req.required_mission_id not in completed_missions
    ]
    for mission_id in missing_explicit:
        reasons.append(f"Завершите миссию «{mission_titles.get(mission_id, '#'+str(mission_id))}»")

    for mission_id in branch_dependencies.get(mission.id, set()):
        if mission_id not in completed_missions:
            reasons.append(
                "Продолжение ветки откроется после миссии «"
                f"{mission_titles.get(mission_id, '#'+str(mission_id))}»"
            )

    is_available = mission.is_active and not reasons
    return is_available, reasons


@router.get("/branches", response_model=list[BranchRead], summary="Список веток миссий")
def list_branches(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[BranchRead]:
    """Возвращаем ветки с упорядоченными миссиями."""

    db.refresh(current_user)
    _ = current_user.submissions
    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions).selectinload(BranchMission.mission))
        .order_by(Branch.title)
        .all()
    )

    completed_missions = _load_user_progress(current_user)
    branch_dependencies = _build_branch_dependencies(branches)

    mission_titles = {
        item.mission_id: item.mission.title if item.mission else ""
        for branch in branches
        for item in branch.missions
    }
    mission_titles.update(dict(db.query(Mission.id, Mission.title).all()))

    response: list[BranchRead] = []
    for branch in branches:
        ordered_links = sorted(branch.missions, key=lambda link: link.order)
        completed_count = sum(1 for link in ordered_links if link.mission_id in completed_missions)
        total = len(ordered_links)

        missions_payload = []
        for link in ordered_links:
            mission_obj = link.mission
            mission_title = mission_obj.title if mission_obj else ""
            is_completed = link.mission_id in completed_missions
            if mission_obj:
                is_available, _ = _mission_availability(
                    mission=mission_obj,
                    user=current_user,
                    completed_missions=completed_missions,
                    branch_dependencies=branch_dependencies,
                    mission_titles=mission_titles,
                )
            else:
                is_available = False
            missions_payload.append(
                BranchMissionRead(
                    mission_id=link.mission_id,
                    mission_title=mission_title,
                    order=link.order,
                    is_completed=is_completed,
                    is_available=is_available,
                )
            )

        response.append(
            BranchRead(
                id=branch.id,
                title=branch.title,
                description=branch.description,
                category=branch.category,
                missions=missions_payload,
                total_missions=total,
                completed_missions=completed_count,
            )
        )

    return response


@router.get("/", response_model=list[MissionBase], summary="Список миссий")
def list_missions(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[MissionBase]:
    """Возвращаем доступные миссии."""

    db.refresh(current_user)
    _ = current_user.submissions

    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions))
        .all()
    )
    branch_dependencies = _build_branch_dependencies(branches)

    missions = (
        db.query(Mission)
        .options(
            selectinload(Mission.prerequisites),
            selectinload(Mission.minimum_rank),
        )
        .filter(Mission.is_active.is_(True))
        .order_by(Mission.id)
        .all()
    )

    mission_titles = {mission.id: mission.title for mission in missions}
    completed_missions = _load_user_progress(current_user)

    response: list[MissionBase] = []
    for mission in missions:
        is_available, reasons = _mission_availability(
            mission=mission,
            user=current_user,
            completed_missions=completed_missions,
            branch_dependencies=branch_dependencies,
            mission_titles=mission_titles,
        )
        dto = MissionBase.model_validate(mission)
        dto.is_available = is_available
        dto.locked_reasons = reasons
        response.append(dto)

    return response


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

    db.refresh(current_user)
    _ = current_user.submissions
    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions))
        .all()
    )
    branch_dependencies = _build_branch_dependencies(branches)
    completed_missions = _load_user_progress(current_user)
    mission_titles = dict(db.query(Mission.id, Mission.title).all())

    is_available, reasons = _mission_availability(
        mission=mission,
        user=current_user,
        completed_missions=completed_missions,
        branch_dependencies=branch_dependencies,
        mission_titles=mission_titles,
    )

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
        is_available=is_available,
        locked_reasons=reasons,
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

    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.is_active.is_(True)).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")

    db.refresh(current_user)
    _ = current_user.submissions
    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions))
        .all()
    )
    branch_dependencies = _build_branch_dependencies(branches)
    completed_missions = _load_user_progress(current_user)
    mission_titles = dict(db.query(Mission.id, Mission.title).all())

    is_available, reasons = _mission_availability(
        mission=mission,
        user=current_user,
        completed_missions=completed_missions,
        branch_dependencies=branch_dependencies,
        mission_titles=mission_titles,
    )
    if not is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="; ".join(reasons))
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
