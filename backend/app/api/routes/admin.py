"""HR-панель и административные действия."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_hr
from app.db.session import get_db
from app.models.artifact import Artifact
from app.models.branch import Branch, BranchMission
from app.models.mission import (
    Mission,
    MissionCompetencyReward,
    MissionPrerequisite,
    MissionSubmission,
    SubmissionStatus,
)
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.store import StoreItem
from app.models.user import Competency, User, UserRole
from app.schemas.artifact import ArtifactCreate, ArtifactRead, ArtifactUpdate
from app.schemas.branch import BranchCreate, BranchMissionRead, BranchRead, BranchUpdate
from app.schemas.mission import (
    MissionBase,
    MissionCreate,
    MissionDetail,
    MissionSubmissionRead,
    MissionUpdate,
)
from app.schemas.rank import (
    RankBase,
    RankCreate,
    RankDetailed,
    RankRequirementCompetency,
    RankRequirementMission,
    RankUpdate,
)
from app.schemas.user import CompetencyBase
from app.schemas.store import StoreItemRead, StoreItemUpdate
from app.services.mission import approve_submission, registration_is_open, reject_submission
from app.services.storage import delete_store_image, save_store_image
from app.services.store import store_item_to_read
from app.schemas.admin_stats import AdminDashboardStats, BranchCompletionStat, SubmissionStats

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _mission_to_detail(mission: Mission) -> MissionDetail:
    """Формируем детальную схему миссии."""

    participant_count = sum(
        1 for submission in mission.submissions if submission.status != SubmissionStatus.REJECTED
    )
    is_registration_open = registration_is_open(mission, participant_count=participant_count)

    return MissionDetail(
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
        registered_participants=participant_count,
        registration_open=is_registration_open,
    )


def _rank_to_detailed(rank: Rank) -> RankDetailed:
    """Формируем ранг со списком требований."""

    return RankDetailed(
        id=rank.id,
        title=rank.title,
        description=rank.description,
        required_xp=rank.required_xp,
        mission_requirements=[
            RankRequirementMission(mission_id=req.mission_id, mission_title=req.mission.title)
            for req in rank.mission_requirements
        ],
        competency_requirements=[
            RankRequirementCompetency(
                competency_id=req.competency_id,
                competency_name=req.competency.name,
                required_level=req.required_level,
            )
            for req in rank.competency_requirements
        ],
        created_at=rank.created_at,
        updated_at=rank.updated_at,
    )


def _branch_to_read(branch: Branch) -> BranchRead:
    """Формируем схему ветки с отсортированными миссиями."""

    missions = sorted(branch.missions, key=lambda item: item.order)
    return BranchRead(
        id=branch.id,
        title=branch.title,
        description=branch.description,
        category=branch.category,
        missions=[
            BranchMissionRead(
                mission_id=item.mission_id,
                mission_title=item.mission.title if item.mission else "",
                order=item.order,
                is_completed=False,
                is_available=True,
            )
            for item in missions
        ],
        total_missions=len(missions),
        completed_missions=0,
    )


def _sanitize_optional(value: str | None) -> str | None:
    """Обрезаем пробелы и заменяем пустые строки на None."""

    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _load_rank(db: Session, rank_id: int) -> Rank:
    """Загружаем ранг с зависимостями."""

    return (
        db.query(Rank)
        .options(
            selectinload(Rank.mission_requirements).selectinload(RankMissionRequirement.mission),
            selectinload(Rank.competency_requirements).selectinload(RankCompetencyRequirement.competency),
        )
        .filter(Rank.id == rank_id)
        .one()
    )


def _load_mission(db: Session, mission_id: int) -> Mission:
    """Загружаем миссию с зависимостями."""

    return (
        db.query(Mission)
        .options(
            selectinload(Mission.prerequisites),
            selectinload(Mission.competency_rewards).selectinload(MissionCompetencyReward.competency),
            selectinload(Mission.branches),
            selectinload(Mission.submissions),
        )
        .filter(Mission.id == mission_id)
        .one()
    )


@router.get("/missions", response_model=list[MissionBase], summary="Миссии (HR)")
def admin_missions(*, db: Session = Depends(get_db), current_user=Depends(require_hr)) -> list[MissionBase]:
    """Список всех миссий для HR."""

    missions = db.query(Mission).order_by(Mission.title).all()
    return [MissionBase.model_validate(mission) for mission in missions]


@router.get("/store/items", response_model=list[StoreItemRead], summary="Товары магазина (HR)")
def admin_store_items(
    *, db: Session = Depends(get_db), current_user=Depends(require_hr)
) -> list[StoreItemRead]:
    """Возвращаем товары магазина для панели HR."""

    items = db.query(StoreItem).order_by(StoreItem.name).all()
    return [store_item_to_read(item) for item in items]


@router.post(
    "/store/items",
    response_model=StoreItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать товар",
)
def admin_store_create(
    name: str = Form(...),
    description: str = Form(...),
    cost_mana: int = Form(...),
    stock: int = Form(...),
    image: UploadFile = File(...),
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> StoreItemRead:
    """Создаём новый товар в магазине."""

    name = name.strip()
    description = description.strip()
    if not name or not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Название и описание не могут быть пустыми",
        )

    try:
        image_path = save_store_image(upload=image)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    item = StoreItem(
        name=name,
        description=description,
        cost_mana=cost_mana,
        stock=stock,
        image_url=image_path,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return store_item_to_read(item)


@router.patch(
    "/store/items/{item_id}",
    response_model=StoreItemRead,
    summary="Обновить товар",
)
def admin_store_update(
    item_id: int,
    item_in: StoreItemUpdate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> StoreItemRead:
    """Редактируем существующий товар."""

    item = db.query(StoreItem).filter(StoreItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    update_data = item_in.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] is not None:
        new_name = update_data["name"].strip()
        if not new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Название не может быть пустым",
            )
        item.name = new_name
    if "description" in update_data and update_data["description"] is not None:
        new_description = update_data["description"].strip()
        if not new_description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Описание не может быть пустым",
            )
        item.description = new_description
    if "cost_mana" in update_data and update_data["cost_mana"] is not None:
        item.cost_mana = update_data["cost_mana"]
    if "stock" in update_data and update_data["stock"] is not None:
        item.stock = update_data["stock"]
    if "image_url" in update_data:
        new_value = _sanitize_optional(update_data["image_url"])
        if new_value is None:
            delete_store_image(item.image_url)
        item.image_url = new_value

    db.add(item)
    db.commit()
    db.refresh(item)
    return store_item_to_read(item)


@router.post(
    "/store/items/{item_id}/image",
    response_model=StoreItemRead,
    summary="Обновить изображение товара",
)
def admin_store_update_image(
    item_id: int,
    image: UploadFile = File(...),
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> StoreItemRead:
    """Заменяем изображение товара на загруженный файл."""

    item = db.query(StoreItem).filter(StoreItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")

    try:
        new_path = save_store_image(upload=image)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    old_path = item.image_url
    item.image_url = new_path

    db.add(item)
    db.commit()
    db.refresh(item)

    delete_store_image(old_path)
    return store_item_to_read(item)


@router.get("/missions/{mission_id}", response_model=MissionDetail, summary="Детали миссии")
def admin_mission_detail(
    mission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> MissionDetail:
    """Детальная карточка миссии."""

    mission = (
        db.query(Mission)
        .options(
            selectinload(Mission.prerequisites),
            selectinload(Mission.competency_rewards).selectinload(MissionCompetencyReward.competency),
            selectinload(Mission.branches),
            selectinload(Mission.submissions),
        )
        .filter(Mission.id == mission_id)
        .first()
    )
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")
    return _mission_to_detail(mission)


@router.get("/branches", response_model=list[BranchRead], summary="Ветки миссий")
def admin_branches(*, db: Session = Depends(get_db), current_user=Depends(require_hr)) -> list[BranchRead]:
    """Возвращаем ветки с миссиями."""

    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions).selectinload(BranchMission.mission))
        .order_by(Branch.title)
        .all()
    )
    return [_branch_to_read(branch) for branch in branches]


@router.post("/branches", response_model=BranchRead, summary="Создать ветку")
def create_branch(
    branch_in: BranchCreate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> BranchRead:
    """Создаём новую ветку."""

    branch = Branch(
        title=branch_in.title,
        description=branch_in.description,
        category=branch_in.category,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return _branch_to_read(branch)


@router.put("/branches/{branch_id}", response_model=BranchRead, summary="Обновить ветку")
def update_branch(
    branch_id: int,
    branch_in: BranchUpdate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> BranchRead:
    """Редактируем ветку."""

    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ветка не найдена")

    branch.title = branch_in.title
    branch.description = branch_in.description
    branch.category = branch_in.category

    db.commit()
    db.refresh(branch)
    return _branch_to_read(branch)


@router.get(
    "/competencies",
    response_model=list[CompetencyBase],
    summary="Каталог компетенций",
)
def list_competencies(
    *, db: Session = Depends(get_db), current_user=Depends(require_hr)
) -> list[CompetencyBase]:
    """Справочник компетенций для форм HR."""

    competencies = db.query(Competency).order_by(Competency.name).all()
    return [CompetencyBase.model_validate(competency) for competency in competencies]


@router.get("/artifacts", response_model=list[ArtifactRead], summary="Каталог артефактов")
def list_artifacts(
    *, db: Session = Depends(get_db), current_user=Depends(require_hr)
) -> list[ArtifactRead]:
    """Справочник артефактов."""

    artifacts = db.query(Artifact).order_by(Artifact.name).all()
    return [ArtifactRead.model_validate(artifact) for artifact in artifacts]


@router.get("/stats", response_model=AdminDashboardStats, summary="Сводная аналитика")
def dashboard_stats(
    *, db: Session = Depends(get_db), current_user=Depends(require_hr)
) -> AdminDashboardStats:
    """Основные метрики прогресса и активности пользователей."""

    total_pilots = db.query(User).filter(User.role == UserRole.PILOT).count()
    approved_submissions = db.query(MissionSubmission).filter(
        MissionSubmission.status == SubmissionStatus.APPROVED
    )
    active_pilots = (
        approved_submissions.with_entities(MissionSubmission.user_id).distinct().count()
    )

    completed_counts = approved_submissions.with_entities(
        MissionSubmission.user_id, func.count(MissionSubmission.id)
    ).group_by(MissionSubmission.user_id)

    total_completed = sum(row[1] for row in completed_counts)
    average_completed = total_completed / active_pilots if active_pilots else 0.0

    submission_stats = SubmissionStats(
        pending=db.query(MissionSubmission).filter(MissionSubmission.status == SubmissionStatus.PENDING).count(),
        approved=approved_submissions.count(),
        rejected=db.query(MissionSubmission).filter(MissionSubmission.status == SubmissionStatus.REJECTED).count(),
    )

    branches = (
        db.query(Branch)
        .options(selectinload(Branch.missions))
        .order_by(Branch.title)
        .all()
    )
    branch_stats: list[BranchCompletionStat] = []
    for branch in branches:
        total_missions = len(branch.missions)
        if total_missions == 0 or total_pilots == 0:
            branch_stats.append(
                BranchCompletionStat(branch_id=branch.id, branch_title=branch.title, completion_rate=0.0)
            )
            continue

        approved_count = (
            db.query(func.count(MissionSubmission.id))
            .join(Mission, Mission.id == MissionSubmission.mission_id)
            .join(BranchMission, BranchMission.mission_id == Mission.id)
            .filter(
                BranchMission.branch_id == branch.id,
                MissionSubmission.status == SubmissionStatus.APPROVED,
            )
            .scalar()
        )
        denominator = total_missions * total_pilots
        rate = min(1.0, approved_count / denominator) if denominator else 0.0
        branch_stats.append(
            BranchCompletionStat(branch_id=branch.id, branch_title=branch.title, completion_rate=rate)
        )

    return AdminDashboardStats(
        total_users=total_pilots,
        active_pilots=active_pilots,
        average_completed_missions=round(average_completed, 2),
        submission_stats=submission_stats,
        branch_completion=branch_stats,
    )


@router.post("/artifacts", response_model=ArtifactRead, summary="Создать артефакт")
def create_artifact(
    artifact_in: ArtifactCreate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> ArtifactRead:
    """Добавляем новый артефакт в каталог."""

    artifact = Artifact(
        name=artifact_in.name,
        description=artifact_in.description,
        rarity=artifact_in.rarity,
        image_url=artifact_in.image_url,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return ArtifactRead.model_validate(artifact)


@router.put("/artifacts/{artifact_id}", response_model=ArtifactRead, summary="Обновить артефакт")
def update_artifact(
    artifact_id: int,
    artifact_in: ArtifactUpdate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> ArtifactRead:
    """Редактируем существующий артефакт."""

    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Артефакт не найден")

    payload = artifact_in.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(artifact, field, value)

    db.commit()
    db.refresh(artifact)
    return ArtifactRead.model_validate(artifact)


@router.delete(
    "/artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить артефакт"
)
def delete_artifact(
    artifact_id: int,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> Response:
    """Удаляем артефакт, если он не привязан к миссиям."""

    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Артефакт не найден")

    missions_with_artifact = db.query(Mission).filter(Mission.artifact_id == artifact_id).count()
    if missions_with_artifact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить артефакт, привязанный к миссиям",
        )

    db.delete(artifact)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
        format=mission_in.format,
        event_location=mission_in.event_location,
        event_address=mission_in.event_address,
        event_starts_at=mission_in.event_starts_at,
        event_ends_at=mission_in.event_ends_at,
        registration_deadline=mission_in.registration_deadline,
        registration_url=mission_in.registration_url,
        registration_notes=mission_in.registration_notes,
        capacity=mission_in.capacity,
        contact_person=mission_in.contact_person,
        contact_phone=mission_in.contact_phone,
        minimum_rank_id=mission_in.minimum_rank_id,
        artifact_id=mission_in.artifact_id,
    )
    db.add(mission)
    db.flush()

    for reward in mission_in.competency_rewards:
        mission.competency_rewards.append(
            MissionCompetencyReward(
                mission_id=mission.id,
                competency_id=reward.competency_id,
                level_delta=reward.level_delta,
            )
        )

    for prerequisite_id in mission_in.prerequisite_ids:
        mission.prerequisites.append(
            MissionPrerequisite(mission_id=mission.id, required_mission_id=prerequisite_id)
        )

    if mission_in.branch_id:
        mission.branches.append(
            BranchMission(
                branch_id=mission_in.branch_id,
                mission_id=mission.id,
                order=mission_in.branch_order,
            )
        )

    db.commit()

    mission = _load_mission(db, mission.id)

    return _mission_to_detail(mission)


@router.put("/missions/{mission_id}", response_model=MissionDetail, summary="Обновить миссию")
def update_mission_endpoint(
    mission_id: int,
    mission_in: MissionUpdate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> MissionDetail:
    """Редактируем миссию."""

    mission = (
        db.query(Mission)
        .options(
            selectinload(Mission.prerequisites),
            selectinload(Mission.competency_rewards),
            selectinload(Mission.branches),
        )
        .filter(Mission.id == mission_id)
        .first()
    )
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")

    payload = mission_in.model_dump(exclude_unset=True)

    for attr in [
        "title",
        "description",
        "xp_reward",
        "mana_reward",
        "difficulty",
        "is_active",
        "format",
        "event_location",
        "event_address",
        "event_starts_at",
        "event_ends_at",
        "registration_deadline",
        "registration_url",
        "registration_notes",
        "capacity",
        "contact_person",
        "contact_phone",
    ]:
        if attr in payload:
            setattr(mission, attr, payload[attr])

    if "minimum_rank_id" in payload:
        mission.minimum_rank_id = payload["minimum_rank_id"]

    if "artifact_id" in payload:
        mission.artifact_id = payload["artifact_id"]

    if "competency_rewards" in payload:
        mission.competency_rewards.clear()
        for reward in payload["competency_rewards"]:
            mission.competency_rewards.append(
                MissionCompetencyReward(
                    mission_id=mission.id,
                    competency_id=reward.competency_id,
                    level_delta=reward.level_delta,
                )
            )

    if "prerequisite_ids" in payload:
        mission.prerequisites.clear()
        for prerequisite_id in payload["prerequisite_ids"]:
            mission.prerequisites.append(
                MissionPrerequisite(mission_id=mission.id, required_mission_id=prerequisite_id)
            )

    if "branch_id" in payload:
        mission.branches.clear()
        branch_id = payload["branch_id"]
        if branch_id is not None:
            order = payload.get("branch_order", 1)
            mission.branches.append(
                BranchMission(branch_id=branch_id, mission_id=mission.id, order=order)
            )
    elif "branch_order" in payload and mission.branches:
        mission.branches[0].order = payload["branch_order"]

    db.commit()

    mission = _load_mission(db, mission.id)
    return _mission_to_detail(mission)


@router.get("/ranks", response_model=list[RankBase], summary="Список рангов")
def admin_ranks(*, db: Session = Depends(get_db), current_user=Depends(require_hr)) -> list[RankBase]:
    """Перечень рангов."""

    ranks = db.query(Rank).order_by(Rank.required_xp).all()
    return [RankBase.model_validate(rank) for rank in ranks]


@router.get("/ranks/{rank_id}", response_model=RankDetailed, summary="Детали ранга")
def get_rank(
    rank_id: int,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> RankDetailed:
    """Возвращаем подробную информацию о ранге."""

    try:
        rank = _load_rank(db, rank_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ранг не найден") from exc
    return _rank_to_detailed(rank)


@router.post("/ranks", response_model=RankDetailed, summary="Создать ранг")
def create_rank(
    rank_in: RankCreate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> RankDetailed:
    """Создаём новый ранг с требованиями."""

    rank = Rank(title=rank_in.title, description=rank_in.description, required_xp=rank_in.required_xp)
    db.add(rank)
    db.flush()

    for mission_id in rank_in.mission_ids:
        rank.mission_requirements.append(
            RankMissionRequirement(rank_id=rank.id, mission_id=mission_id)
        )

    for item in rank_in.competency_requirements:
        rank.competency_requirements.append(
            RankCompetencyRequirement(
                rank_id=rank.id,
                competency_id=item.competency_id,
                required_level=item.required_level,
            )
        )

    db.commit()

    rank = _load_rank(db, rank.id)
    return _rank_to_detailed(rank)


@router.put("/ranks/{rank_id}", response_model=RankDetailed, summary="Обновить ранг")
def update_rank(
    rank_id: int,
    rank_in: RankUpdate,
    *,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr),
) -> RankDetailed:
    """Редактируем параметры ранга."""

    rank = (
        db.query(Rank)
        .options(
            selectinload(Rank.mission_requirements),
            selectinload(Rank.competency_requirements),
        )
        .filter(Rank.id == rank_id)
        .first()
    )
    if not rank:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ранг не найден")

    rank.title = rank_in.title
    rank.description = rank_in.description
    rank.required_xp = rank_in.required_xp

    rank.mission_requirements.clear()
    for mission_id in rank_in.mission_ids:
        rank.mission_requirements.append(
            RankMissionRequirement(rank_id=rank.id, mission_id=mission_id)
        )

    rank.competency_requirements.clear()
    for item in rank_in.competency_requirements:
        rank.competency_requirements.append(
            RankCompetencyRequirement(
                rank_id=rank.id,
                competency_id=item.competency_id,
                required_level=item.required_level,
            )
        )

    db.commit()

    rank = _load_rank(db, rank.id)
    return _rank_to_detailed(rank)


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
