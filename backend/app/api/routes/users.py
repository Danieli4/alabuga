"""Маршруты работы с профилем."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rank import Rank
from app.models.user import User, UserRole, UserCompetency
from app.models.mission import SubmissionStatus
from app.models.artifact import Artifact
from app.schemas.progress import ProgressSnapshot
from app.schemas.rank import RankBase
from app.schemas.user import (
    LeaderboardEntry,
    ProfilePhotoResponse,
    UserCompetencyRead,
    UserProfile,
)
from app.schemas.artifact import ArtifactRead
from app.services.rank import build_progress_snapshot
from app.services.storage import (
    build_photo_data_url,
    delete_profile_photo,
    save_profile_photo,
)

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

    profile = UserProfile.model_validate(current_user)
    profile.profile_photo_uploaded = bool(current_user.profile_photo_path)
    profile.profile_photo_updated_at = (
        current_user.updated_at if current_user.profile_photo_path else None
    )
    return profile


@router.get(
    "/me/photo",
    response_model=ProfilePhotoResponse,
    summary="Получаем фото профиля кандидата",
)
def get_profile_photo(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ProfilePhotoResponse:
    """Читаем сохранённое изображение и возвращаем его в виде data URL."""

    db.refresh(current_user)
    if not current_user.profile_photo_path:
        return ProfilePhotoResponse(photo=None, detail="Фотография не загружена")

    try:
        photo = build_photo_data_url(current_user.profile_photo_path)
    except FileNotFoundError:
        # Если файл удалили вручную, сбрасываем ссылку в базе, чтобы не мешать пользователю загрузить новую.
        current_user.profile_photo_path = None
        db.add(current_user)
        db.commit()
        return ProfilePhotoResponse(photo=None, detail="Файл не найден")

    return ProfilePhotoResponse(photo=photo)


@router.post(
    "/me/photo",
    response_model=ProfilePhotoResponse,
    status_code=status.HTTP_200_OK,
    summary="Загружаем фото профиля",
)
def upload_profile_photo(
    photo: UploadFile = File(...),
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfilePhotoResponse:
    """Сохраняем изображение и возвращаем обновлённый data URL."""

    try:
        relative_path = save_profile_photo(upload=photo, user_id=current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    delete_profile_photo(current_user.profile_photo_path)
    current_user.profile_photo_path = relative_path
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    photo_url = build_photo_data_url(relative_path)
    return ProfilePhotoResponse(photo=photo_url, detail="Фотография обновлена")


@router.delete(
    "/me/photo",
    response_model=ProfilePhotoResponse,
    summary="Удаляем фото профиля",
)
def delete_profile_photo_endpoint(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ProfilePhotoResponse:
    """Удаляем сохранённое фото и очищаем ссылку в профиле."""

    if not current_user.profile_photo_path:
        return ProfilePhotoResponse(photo=None, detail="Фотография уже удалена")

    delete_profile_photo(current_user.profile_photo_path)
    current_user.profile_photo_path = None
    db.add(current_user)
    db.commit()

    return ProfilePhotoResponse(photo=None, detail="Фотография удалена")


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


@router.post("/me/apply-artifact/{artifact_id}", summary="Применить артефакт-модификатор")
def apply_artifact(
    artifact_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Применяет артефакт-модификатор к профилю пользователя."""
    
    # Проверяем, что артефакт существует и является модификатором
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Артефакт не найден")
    
    if not artifact.is_profile_modifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот артефакт не является модификатором профиля"
        )
    
    # Проверяем, что у пользователя есть этот артефакт
    user_artifact = db.query(User).join(User.artifacts).filter(
        User.id == current_user.id,
        User.artifacts.any(artifact_id=artifact_id)
    ).first()
    
    if not user_artifact:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет этого артефакта"
        )
    
    # Получаем список применённых артефактов
    applied_ids = []
    if current_user.applied_artifact_ids:
        applied_ids = [int(x) for x in current_user.applied_artifact_ids.split(",") if x]
    
    # Проверяем, не применён ли уже
    if artifact_id in applied_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот артефакт уже применён"
        )
    
    # Применяем артефакт
    applied_ids.append(artifact_id)
    current_user.applied_artifact_ids = ",".join(map(str, applied_ids))
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Артефакт успешно применён",
        "artifact_id": artifact_id,
        "applied_artifacts": applied_ids
    }


@router.delete("/me/unapply-artifact/{artifact_id}", summary="Снять артефакт-модификатор")
def unapply_artifact(
    artifact_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Снимает артефакт-модификатор с профиля пользователя."""
    
    # Получаем список применённых артефактов
    applied_ids = []
    if current_user.applied_artifact_ids:
        applied_ids = [int(x) for x in current_user.applied_artifact_ids.split(",") if x]
    
    if artifact_id not in applied_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот артефакт не применён"
        )
    
    # Снимаем артефакт
    applied_ids.remove(artifact_id)
    current_user.applied_artifact_ids = ",".join(map(str, applied_ids)) if applied_ids else None
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Артефакт успешно снят",
        "artifact_id": artifact_id,
        "applied_artifacts": applied_ids
    }


@router.get("/me/applied-artifacts", response_model=list[ArtifactRead], summary="Получить применённые артефакты")
def get_applied_artifacts(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[ArtifactRead]:
    """Возвращает список применённых артефактов-модификаторов."""
    
    if not current_user.applied_artifact_ids:
        return []
    
    applied_ids = [int(x) for x in current_user.applied_artifact_ids.split(",") if x]
    
    artifacts = db.query(Artifact).filter(Artifact.id.in_(applied_ids)).all()
    
    return [ArtifactRead.model_validate(artifact) for artifact in artifacts]
