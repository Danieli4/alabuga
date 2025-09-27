"""Правила повышения ранга."""

from __future__ import annotations

from sqlalchemy.orm import Session, selectinload

from app.models.journal import JournalEventType
from app.models.mission import SubmissionStatus
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.user import User
from app.services.journal import log_event
from app.schemas.progress import (
    ProgressCompetencyRequirement,
    ProgressMissionRequirement,
    ProgressRank,
    ProgressSnapshot,
    ProgressXPMetrics,
)


def _eligible_rank(user: User, db: Session) -> Rank | None:
    """Определяем максимальный ранг, который доступен пользователю."""

    ranks = db.query(Rank).order_by(Rank.required_xp).all()
    approved_missions = {
        submission.mission_id
        for submission in user.submissions
        if submission.status == SubmissionStatus.APPROVED
    }
    competencies = {c.competency_id: c.level for c in user.competencies}

    candidate: Rank | None = None
    for rank in ranks:
        if user.xp < rank.required_xp:
            break

        missions_ok = all(req.mission_id in approved_missions for req in rank.mission_requirements)
        competencies_ok = all(
            competencies.get(req.competency_id, 0) >= req.required_level
            for req in rank.competency_requirements
        )
        if missions_ok and competencies_ok:
            candidate = rank

    return candidate


def apply_rank_upgrade(user: User, db: Session) -> Rank | None:
    """Пытаемся повысить ранг и фиксируем событие."""

    new_rank = _eligible_rank(user, db)
    if not new_rank or user.current_rank_id == new_rank.id:
        return None

    previous_rank_id = user.current_rank_id
    user.current_rank_id = new_rank.id
    db.add(user)
    db.commit()
    db.refresh(user)

    log_event(
        db,
        user_id=user.id,
        event_type=JournalEventType.RANK_UP,
        title="Повышение ранга",
        description=f"Пилот достиг ранга «{new_rank.title}».",
        payload={"previous_rank_id": previous_rank_id, "new_rank_id": new_rank.id},
    )
    return new_rank


def build_progress_snapshot(user: User, db: Session) -> ProgressSnapshot:
    """Собираем агрегированное представление прогресса пользователя."""

    ranks = (
        db.query(Rank)
        .options(
            selectinload(Rank.mission_requirements).selectinload(RankMissionRequirement.mission),
            selectinload(Rank.competency_requirements).selectinload(RankCompetencyRequirement.competency),
        )
        .order_by(Rank.required_xp)
        .all()
    )

    current_rank_obj = next((rank for rank in ranks if rank.id == user.current_rank_id), None)

    approved_missions = {
        submission.mission_id
        for submission in user.submissions
        if submission.status == SubmissionStatus.APPROVED
    }
    competency_levels = {item.competency_id: item.level for item in user.competencies}

    highest_met_rank: Rank | None = None
    next_rank_obj: Rank | None = None
    for rank in ranks:
        missions_ok = all(req.mission_id in approved_missions for req in rank.mission_requirements)
        competencies_ok = all(
            competency_levels.get(req.competency_id, 0) >= req.required_level
            for req in rank.competency_requirements
        )
        xp_ok = user.xp >= rank.required_xp

        if xp_ok and missions_ok and competencies_ok:
            highest_met_rank = rank
            continue

        if next_rank_obj is None:
            next_rank_obj = rank
        break

    baseline_rank = current_rank_obj or highest_met_rank
    baseline_xp = baseline_rank.required_xp if baseline_rank else 0

    if next_rank_obj:
        target_xp = next_rank_obj.required_xp
        remaining_xp = max(0, target_xp - user.xp)
        denominator = max(target_xp - baseline_xp, 1)
        progress_percent = min(1.0, max(0.0, (user.xp - baseline_xp) / denominator))
    else:
        target_xp = max(user.xp, baseline_xp)
        remaining_xp = 0
        progress_percent = 1.0

    mission_requirements: list[ProgressMissionRequirement] = []
    if next_rank_obj:
        for requirement in next_rank_obj.mission_requirements:
            title = requirement.mission.title if requirement.mission else f"Миссия #{requirement.mission_id}"
            mission_requirements.append(
                ProgressMissionRequirement(
                    mission_id=requirement.mission_id,
                    mission_title=title,
                    is_completed=requirement.mission_id in approved_missions,
                )
            )

    competency_requirements: list[ProgressCompetencyRequirement] = []
    if next_rank_obj:
        for requirement in next_rank_obj.competency_requirements:
            current_level = competency_levels.get(requirement.competency_id, 0)
            competency_requirements.append(
                ProgressCompetencyRequirement(
                    competency_id=requirement.competency_id,
                    competency_name=requirement.competency.name if requirement.competency else "",
                    required_level=requirement.required_level,
                    current_level=current_level,
                    is_met=current_level >= requirement.required_level,
                )
            )

    completed_missions = sum(1 for item in mission_requirements if item.is_completed)
    met_competencies = sum(1 for item in competency_requirements if item.is_met)

    xp_metrics = ProgressXPMetrics(
        baseline=baseline_xp,
        current=user.xp,
        target=target_xp,
        remaining=remaining_xp,
        progress_percent=round(progress_percent, 4),
    )

    return ProgressSnapshot(
        current_rank=ProgressRank.model_validate(current_rank_obj) if current_rank_obj else None,
        next_rank=ProgressRank.model_validate(next_rank_obj) if next_rank_obj else None,
        xp=xp_metrics,
        mission_requirements=mission_requirements,
        competency_requirements=competency_requirements,
        completed_missions=completed_missions,
        total_missions=len(mission_requirements),
        met_competencies=met_competencies,
        total_competencies=len(competency_requirements),
    )
