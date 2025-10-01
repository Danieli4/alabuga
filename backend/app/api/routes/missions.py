"""Маршруты для работы с миссиями."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.coding import CodingAttempt, CodingChallenge
from app.models.branch import Branch, BranchMission
from app.models.mission import Mission, MissionSubmission, SubmissionStatus
from app.models.user import User, UserRole
from app.models.python import PythonChallenge, PythonUserProgress
from app.schemas.branch import BranchMissionRead, BranchRead
from app.schemas.mission import (
    MissionBase,
    MissionDetail,
    MissionSubmissionRead,
)
from app.schemas.coding import (
    CodingChallengeState,
    CodingMissionState,
    CodingRunRequest,
    CodingRunResponse,
)
from app.services.coding import count_completed_challenges, evaluate_challenge
from app.services.mission import UNSET, registration_is_open, submit_mission
from app.services.storage import delete_submission_document, save_submission_document
from app.core.config import settings

router = APIRouter(prefix="/api/missions", tags=["missions"])

# Для миссии #1 требуется обязательное прикрепление документов.
REQUIRED_DOCUMENT_MISSIONS = {1}


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


def _ensure_mission_access(
    *,
    mission: Mission,
    user: User,
    db: Session,
) -> tuple[bool, set[int]]:
    """Проверяем, что миссия активна и доступна пилоту."""

    db.refresh(user)
    _ = user.submissions

    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions))
        .all()
    )
    branch_dependencies = _build_branch_dependencies(branches)
    completed_missions = _load_user_progress(user)
    mission_titles = dict(db.query(Mission.id, Mission.title).all())

    is_available, reasons = _mission_availability(
        mission=mission,
        user=user,
        completed_missions=completed_missions,
        branch_dependencies=branch_dependencies,
        mission_titles=mission_titles,
    )

    if mission.id not in completed_missions and not is_available:
        message = reasons[0] if reasons else "Миссия пока недоступна."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return mission.id in completed_missions, completed_missions


def _build_challenge_state(
    *,
    challenges: list[CodingChallenge],
    attempts: list[CodingAttempt],
) -> tuple[list[CodingChallengeState], int, int, int | None]:
    """Формируем состояние каждого задания."""

    latest_attempts: dict[int, CodingAttempt] = {}
    completed_ids: set[int] = set()

    for attempt in sorted(attempts, key=lambda item: item.created_at, reverse=True):
        if attempt.challenge_id not in latest_attempts:
            latest_attempts[attempt.challenge_id] = attempt
        if attempt.is_passed:
            completed_ids.add(attempt.challenge_id)

    completed_count = len(completed_ids)
    total = len(challenges)

    states: list[CodingChallengeState] = []
    current_id: int | None = None

    for challenge in challenges:
        last_attempt = latest_attempts.get(challenge.id)
        is_passed = challenge.id in completed_ids
        is_unlocked = is_passed

        if not is_passed and current_id is None:
            current_id = challenge.id
            is_unlocked = True

        states.append(
            CodingChallengeState(
                id=challenge.id,
                order=challenge.order,
                title=challenge.title,
                prompt=challenge.prompt,
                starter_code=challenge.starter_code,
                is_passed=is_passed,
                is_unlocked=is_unlocked,
                last_submitted_code=last_attempt.code if last_attempt else None,
                last_stdout=last_attempt.stdout if last_attempt else None,
                last_stderr=last_attempt.stderr if last_attempt else None,
                last_exit_code=last_attempt.exit_code if last_attempt else None,
                updated_at=last_attempt.updated_at if last_attempt else None,
            )
        )

    return states, total, completed_count, current_id

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
            selectinload(Mission.coding_challenges),
        )
        .filter(Mission.is_active.is_(True))
        .order_by(Mission.id)
        .all()
    )

    mission_titles = {mission.id: mission.title for mission in missions}
    completed_missions = _load_user_progress(current_user)
    submission_status_map = {
        submission.mission_id: submission.status for submission in current_user.submissions
    }
    coding_progress = count_completed_challenges(
        db,
        mission_ids=[mission.id for mission in missions if mission.coding_challenges],
        user=current_user,
    )

    mission_ids = [mission.id for mission in missions]
    registration_counts = {
        mission_id: count
        for mission_id, count in (
            db.query(MissionSubmission.mission_id, func.count(MissionSubmission.id))
            .filter(
                MissionSubmission.mission_id.in_(mission_ids),
                MissionSubmission.status != SubmissionStatus.REJECTED,
            )
            .group_by(MissionSubmission.mission_id)
            .all()
        )
    }

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
        dto.requires_documents = mission.id in REQUIRED_DOCUMENT_MISSIONS
        if mission.id in completed_missions:
            dto.is_completed = True
            dto.is_available = False
            dto.locked_reasons = ["Миссия уже завершена"]
        else:
            dto.is_completed = False
            dto.is_available = is_available
            dto.locked_reasons = reasons
        dto.has_coding_challenges = bool(mission.coding_challenges)
        dto.coding_challenge_count = len(mission.coding_challenges)
        dto.completed_coding_challenges = coding_progress.get(mission.id, 0)
        dto.submission_status = submission_status_map.get(mission.id)
        participants = registration_counts.get(mission.id, 0)
        dto.registered_participants = participants
        dto.registration_open = registration_is_open(
            mission,
            participant_count=participants,
            now=datetime.now(timezone.utc),
        )
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

    mission = (
        db.query(Mission)
        .options(selectinload(Mission.coding_challenges))
        .filter(Mission.id == mission_id, Mission.is_active.is_(True))
        .first()
    )
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
    coding_progress = count_completed_challenges(db, mission_ids=[mission.id], user=current_user)

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
        format=mission.format,
        event_location=mission.event_location,
        event_address=mission.event_address,
        event_starts_at=mission.event_starts_at,
        event_ends_at=mission.event_ends_at,
        registration_deadline=mission.registration_deadline,
        registration_url=mission.registration_url,
        registration_notes=mission.registration_notes,
        capacity=mission.capacity,
        contact_person=mission.contact_person,
        contact_phone=mission.contact_phone,
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
    data.requires_documents = mission.id in REQUIRED_DOCUMENT_MISSIONS
    data.has_coding_challenges = bool(mission.coding_challenges)
    data.coding_challenge_count = len(mission.coding_challenges)
    data.completed_coding_challenges = coding_progress.get(mission.id, 0)
    data.submission_status = next(
        (submission.status for submission in current_user.submissions if submission.mission_id == mission.id),
        None,
    )
    participant_count = (
        db.query(MissionSubmission)
        .filter(
            MissionSubmission.mission_id == mission.id,
            MissionSubmission.status != SubmissionStatus.REJECTED,
        )
        .count()
    )
    data.registered_participants = participant_count
    data.registration_open = registration_is_open(
        mission,
        participant_count=participant_count,
        now=datetime.now(timezone.utc),
    )
    if mission.id in completed_missions:
        data.is_completed = True
        data.is_available = False
        data.locked_reasons = ["Миссия уже завершена"]
    return data


@router.get(
    "/{mission_id}/coding/challenges",
    response_model=CodingMissionState,
    summary="Получаем список заданий по Python",
)
def get_coding_challenges(
    mission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CodingMissionState:
    """Возвращаем состояние миссии с программированием."""

    mission = (
        db.query(Mission)
        .options(selectinload(Mission.coding_challenges))
        .filter(Mission.id == mission_id, Mission.is_active.is_(True))
        .first()
    )
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")

    if not mission.coding_challenges:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Для миссии не настроены задания на программирование.",
        )

    mission_completed, completed_missions = _ensure_mission_access(
        mission=mission,
        user=current_user,
        db=db,
    )

    challenge_ids = [challenge.id for challenge in mission.coding_challenges]
    attempts: list[CodingAttempt] = []
    if challenge_ids:
        attempts = (
            db.query(CodingAttempt)
            .filter(
                CodingAttempt.user_id == current_user.id,
                CodingAttempt.challenge_id.in_(challenge_ids),
            )
            .order_by(CodingAttempt.created_at.desc())
            .all()
        )

    states, total, completed_count, current_id = _build_challenge_state(
        challenges=sorted(mission.coding_challenges, key=lambda item: item.order),
        attempts=attempts,
    )

    if mission.id in completed_missions:
        mission_completed = True

    return CodingMissionState(
        mission_id=mission.id,
        total_challenges=total,
        completed_challenges=completed_count,
        current_challenge_id=current_id,
        is_mission_completed=mission_completed,
        challenges=states,
    )


@router.post(
    "/{mission_id}/coding/challenges/{challenge_id}/run",
    response_model=CodingRunResponse,
    summary="Проверяем решение задания",
)
def run_coding_challenge(
    mission_id: int,
    challenge_id: int,
    payload: CodingRunRequest,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CodingRunResponse:
    """Запускаем Python-код кандидата и возвращаем результат."""

    mission = (
        db.query(Mission)
        .options(selectinload(Mission.coding_challenges))
        .filter(Mission.id == mission_id, Mission.is_active.is_(True))
        .first()
    )
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")

    mission_completed, _ = _ensure_mission_access(mission=mission, user=current_user, db=db)

    challenge = next((item for item in mission.coding_challenges if item.id == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задание не найдено")

    evaluation = evaluate_challenge(
        db,
        challenge=challenge,
        user=current_user,
        code=payload.code,
    )

    mission_completed = mission_completed or evaluation.mission_completed
    expected_output = None
    if not evaluation.attempt.is_passed:
        expected_output = challenge.expected_output

    return CodingRunResponse(
        attempt_id=evaluation.attempt.id,
        stdout=evaluation.attempt.stdout,
        stderr=evaluation.attempt.stderr,
        exit_code=evaluation.attempt.exit_code,
        is_passed=evaluation.attempt.is_passed,
        mission_completed=mission_completed,
        expected_output=expected_output,
    )


@router.post("/{mission_id}/submit", response_model=MissionSubmissionRead, summary="Отправляем отчёт")
async def submit(
    mission_id: int,
    *,
    comment: str | None = Form(None),
    proof_url: str | None = Form(None),
    resume_link: str | None = Form(None),
    passport: UploadFile | None = File(None),
    photo: UploadFile | None = File(None),
    resume_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MissionSubmissionRead:
    """Пилот отправляет доказательство выполнения миссии и сопроводительные документы."""

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

    existing_submission = (
        db.query(MissionSubmission)
        .filter(MissionSubmission.user_id == current_user.id, MissionSubmission.mission_id == mission.id)
        .first()
    )

    participant_count = (
        db.query(MissionSubmission)
        .filter(
            MissionSubmission.mission_id == mission.id,
            MissionSubmission.status != SubmissionStatus.REJECTED,
        )
        .count()
    )
    registration_open_state = registration_is_open(
        mission,
        participant_count=participant_count,
        now=datetime.now(timezone.utc),
    )
    if not registration_open_state and not existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Регистрация на офлайн-мероприятие закрыта.",
        )

    def _has_upload(upload: UploadFile | None) -> bool:
        return bool(upload and upload.filename)

    passport_required = mission.id in REQUIRED_DOCUMENT_MISSIONS
    photo_required = mission.id in REQUIRED_DOCUMENT_MISSIONS
    resume_required = mission.id in REQUIRED_DOCUMENT_MISSIONS

    if passport_required and not (
        (existing_submission and existing_submission.passport_path) or _has_upload(passport)
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Загрузите скан паспорта кандидата.")

    if photo_required and not (
        (existing_submission and existing_submission.photo_path) or _has_upload(photo)
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Добавьте актуальную фотографию кандидата.")

    existing_resume_sources = bool(
        existing_submission
        and (existing_submission.resume_path or existing_submission.resume_link)
    )
    resume_link_trimmed = (resume_link or "").strip()
    resume_file_provided = _has_upload(resume_file)
    if resume_required and not (existing_resume_sources or resume_link_trimmed or resume_file_provided):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Добавьте ссылку на резюме или загрузите файл с резюме.",
        )

    new_passport_path = None
    new_photo_path = None
    new_resume_path = None

    try:
        if _has_upload(passport):
            new_passport_path = save_submission_document(
                upload=passport,
                user_id=current_user.id,
                mission_id=mission.id,
                kind="passport",
            )

        if _has_upload(photo):
            new_photo_path = save_submission_document(
                upload=photo,
                user_id=current_user.id,
                mission_id=mission.id,
                kind="photo",
            )

        if resume_file_provided:
            new_resume_path = save_submission_document(
                upload=resume_file,
                user_id=current_user.id,
                mission_id=mission.id,
                kind="resume",
            )

        submission = submit_mission(
            db=db,
            user=current_user,
            mission=mission,
            comment=(comment or "").strip() or None,
            proof_url=(proof_url or "").strip() or None,
            passport_path=new_passport_path if new_passport_path is not None else UNSET,
            photo_path=new_photo_path if new_photo_path is not None else UNSET,
            resume_path=new_resume_path if new_resume_path is not None else UNSET,
            resume_link=(resume_link_trimmed or None) if resume_link is not None else UNSET,
        )
    except Exception:
        delete_submission_document(new_passport_path)
        delete_submission_document(new_photo_path)
        delete_submission_document(new_resume_path)
        raise

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


@router.get(
    "/submissions/{submission_id}/files/{document}",
    summary="Скачиваем загруженные файлы",
)
def download_submission_file(
    submission_id: int,
    document: str,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """Возвращаем файл паспорта, фото или резюме."""

    submission = db.query(MissionSubmission).filter(MissionSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отправка не найдена")

    if submission.user_id != current_user.id and current_user.role != UserRole.HR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к файлу")

    attribute_map = {
        "passport": submission.passport_path,
        "photo": submission.photo_path,
        "resume": submission.resume_path,
    }

    relative_path = attribute_map.get(document)
    if not relative_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    file_path = settings.uploads_path / relative_path
    resolved = file_path.resolve()
    base = settings.uploads_path.resolve()
    if not resolved.is_relative_to(base):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    if not resolved.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    return FileResponse(resolved, filename=resolved.name)
