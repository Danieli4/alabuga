"""Маршруты для работы с миссиями."""

from __future__ import annotations

from collections import defaultdict
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
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
from app.services.mission import UNSET, submit_mission
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
        dto.requires_documents = mission.id in REQUIRED_DOCUMENT_MISSIONS
        if mission.id in completed_missions:
            dto.is_completed = True
            dto.is_available = False
            dto.locked_reasons = ["Миссия уже завершена"]
        else:
            dto.is_completed = False
            dto.is_available = is_available
            dto.locked_reasons = reasons

        total_python = (
            db.query(PythonChallenge)
            .filter(PythonChallenge.mission_id == mission.id)
            .count()
        )
        if total_python:
            progress = (
                db.query(PythonUserProgress)
                .filter(
                    PythonUserProgress.user_id == current_user.id,
                    PythonUserProgress.mission_id == mission.id,
                )
                .first()
            )
            dto.python_challenges_total = total_python
            dto.python_completed_challenges = progress.current_order if progress else 0
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
    data.requires_documents = mission.id in REQUIRED_DOCUMENT_MISSIONS

    total_python = (
        db.query(PythonChallenge)
        .filter(PythonChallenge.mission_id == mission.id)
        .count()
    )
    if total_python:
        progress = (
            db.query(PythonUserProgress)
            .filter(
                PythonUserProgress.user_id == current_user.id,
                PythonUserProgress.mission_id == mission.id,
            )
            .first()
        )
        data.python_challenges_total = total_python
        data.python_completed_challenges = progress.current_order if progress else 0
        if progress and progress.current_order >= total_python:
            data.is_completed = True
            data.is_available = False
            data.locked_reasons = ["Миссия уже завершена"]

    if mission.id in completed_missions:
        data.is_completed = True
        data.is_available = False
        data.locked_reasons = ["Миссия уже завершена"]
    return data


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
