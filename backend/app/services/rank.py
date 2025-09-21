"""Правила повышения ранга."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.journal import JournalEventType
from app.models.mission import SubmissionStatus
from app.models.rank import Rank
from app.models.user import User
from app.services.journal import log_event


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
