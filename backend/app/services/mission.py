"""Бизнес-логика работы с миссиями."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.journal import JournalEventType
from app.models.mission import (
    Mission,
    MissionFormat,
    MissionRegistration,
    MissionSubmission,
    SubmissionStatus,
)
from app.models.user import User, UserArtifact, UserCompetency
from app.services.journal import log_event
from app.services.rank import apply_rank_upgrade
from app.services.storage import delete_submission_document


UNSET: Any = object()


def _ensure_aware(value: datetime | None) -> datetime | None:
    """SQLite возвращает наивные datetime — приводим их к UTC."""

    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def registration_is_open(
    mission: Mission,
    *,
    now: datetime | None = None,
    registered_count: int | None = None,
) -> bool:
    """Проверяем, доступна ли запись на офлайн-мероприятие."""

    if mission.format != MissionFormat.OFFLINE:
        return False

    current_time = now or datetime.now(timezone.utc)

    deadline = _ensure_aware(mission.registration_deadline)
    start_at = _ensure_aware(mission.starts_at)

    if deadline and deadline < current_time:
        return False

    if start_at and start_at < current_time:
        return False

    if mission.capacity is not None:
        count = registered_count if registered_count is not None else len(mission.registrations)
        if count >= mission.capacity:
            return False

    return True


def register_for_offline_mission(
    *,
    db: Session,
    user: User,
    mission: Mission,
) -> MissionRegistration:
    """Регистрируем пилота на офлайн-миссию."""

    if mission.format != MissionFormat.OFFLINE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Это онлайн-миссия")

    existing = (
        db.query(MissionRegistration)
        .filter(
            MissionRegistration.mission_id == mission.id,
            MissionRegistration.user_id == user.id,
        )
        .first()
    )
    if existing:
        return existing

    registered_count = (
        db.query(MissionRegistration)
        .filter(MissionRegistration.mission_id == mission.id)
        .count()
    )

    if mission.capacity is not None and registered_count >= mission.capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Свободные места закончились")

    now = datetime.now(timezone.utc)
    deadline = _ensure_aware(mission.registration_deadline)
    start_at = _ensure_aware(mission.starts_at)

    if deadline and deadline < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Регистрация завершена")
    if start_at and start_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Мероприятие уже началось")

    registration = MissionRegistration(mission_id=mission.id, user_id=user.id)
    db.add(registration)
    db.commit()
    db.refresh(registration)

    log_event(
        db,
        user_id=user.id,
        event_type=JournalEventType.MISSION_COMPLETED,
        title=f"Заявка на мероприятие «{mission.title}» отправлена",
        description="Вы записались на офлайн-мероприятие. Напоминание придёт ближе к дате.",
        payload={"mission_id": mission.id},
    )

    return registration


def submit_mission(
    *,
    db: Session,
    user: User,
    mission: Mission,
    comment: str | None,
    proof_url: str | None,
    passport_path: Any = UNSET,
    photo_path: Any = UNSET,
    resume_path: Any = UNSET,
    resume_link: Any = UNSET,
) -> MissionSubmission:
    """Создаём или обновляем отправку."""

    submission = (
        db.query(MissionSubmission)
        .filter(MissionSubmission.user_id == user.id, MissionSubmission.mission_id == mission.id)
        .first()
    )
    if submission and submission.status == SubmissionStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Миссия уже зачтена")

    if not submission:
        submission = MissionSubmission(user_id=user.id, mission_id=mission.id)

    submission.comment = comment
    submission.proof_url = proof_url

    if passport_path is not UNSET:
        if isinstance(passport_path, str) and submission.passport_path and submission.passport_path != passport_path:
            delete_submission_document(submission.passport_path)
        submission.passport_path = passport_path if isinstance(passport_path, str) else None

    if photo_path is not UNSET:
        if isinstance(photo_path, str) and submission.photo_path and submission.photo_path != photo_path:
            delete_submission_document(submission.photo_path)
        submission.photo_path = photo_path if isinstance(photo_path, str) else None

    if resume_path is not UNSET:
        if isinstance(resume_path, str) and submission.resume_path and submission.resume_path != resume_path:
            delete_submission_document(submission.resume_path)
        submission.resume_path = resume_path if isinstance(resume_path, str) else None

    if resume_link is not UNSET:
        submission.resume_link = resume_link if isinstance(resume_link, str) else None

    submission.status = SubmissionStatus.PENDING

    db.add(submission)
    db.commit()
    db.refresh(submission)

    log_event(
        db,
        user_id=user.id,
        event_type=JournalEventType.MISSION_COMPLETED,
        title=f"Отправка миссии «{mission.title}»",
        description="Отчёт отправлен и ожидает проверки.",
        payload={"mission_id": mission.id},
    )

    return submission


def _increase_competencies(db: Session, user: User, mission: Mission) -> None:
    """Повышаем уровни компетенций за миссию."""

    for reward in mission.competency_rewards:
        user_competency = next(
            (uc for uc in user.competencies if uc.competency_id == reward.competency_id),
            None,
        )
        if not user_competency:
            user_competency = UserCompetency(
                user_id=user.id, competency_id=reward.competency_id, level=0
            )
            db.add(user_competency)
            db.flush()
        user_competency.level += reward.level_delta
        db.add(user_competency)


def approve_submission(db: Session, submission: MissionSubmission) -> MissionSubmission:
    """Подтверждаем миссию, начисляем награды и проверяем ранг."""

    if submission.status == SubmissionStatus.APPROVED:
        return submission

    submission.status = SubmissionStatus.APPROVED
    submission.awarded_xp = submission.mission.xp_reward
    submission.awarded_mana = submission.mission.mana_reward

    user = submission.user
    user.xp += submission.awarded_xp
    user.mana += submission.awarded_mana

    _increase_competencies(db, user, submission.mission)

    if submission.mission.artifact_id:
        already_has = any(
            artifact.artifact_id == submission.mission.artifact_id for artifact in user.artifacts
        )
        if not already_has:
            db.add(UserArtifact(user_id=user.id, artifact_id=submission.mission.artifact_id))
            log_event(
                db,
                user_id=user.id,
                event_type=JournalEventType.MISSION_COMPLETED,
                title=f"Получен артефакт за миссию «{submission.mission.title}»",
                description="Новый артефакт добавлен в коллекцию.",
                payload={"artifact_id": submission.mission.artifact_id},
            )

    db.add_all([submission, user])
    db.commit()
    db.refresh(submission)

    log_event(
        db,
        user_id=user.id,
        event_type=JournalEventType.MISSION_COMPLETED,
        title=f"Миссия «{submission.mission.title}» подтверждена",
        description="HR одобрил выполнение миссии.",
        payload={"mission_id": submission.mission_id},
        xp_delta=submission.awarded_xp,
        mana_delta=submission.awarded_mana,
    )

    apply_rank_upgrade(user, db)

    return submission


def reject_submission(db: Session, submission: MissionSubmission, comment: str | None = None) -> MissionSubmission:
    """Отклоняем миссию."""

    submission.status = SubmissionStatus.REJECTED
    if comment:
        submission.comment = comment
    db.add(submission)
    db.commit()
    db.refresh(submission)

    log_event(
        db,
        user_id=submission.user_id,
        event_type=JournalEventType.MISSION_COMPLETED,
        title=f"Миссия «{submission.mission.title}» отклонена",
        description=comment or "Проверьте отчёт и отправьте снова.",
        payload={"mission_id": submission.mission_id},
    )

    return submission
