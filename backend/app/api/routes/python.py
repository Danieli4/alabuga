"""API для миссии "Основы Python"."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.mission import Mission
from app.models.user import User
from app.schemas.python import PythonMissionState, PythonSubmitRequest, PythonSubmissionRead
from app.services.python_mission import build_state, submit_code

router = APIRouter(prefix="/api/python-mission", tags=["python-mission"])


def _get_mission(db: Session, mission_id: int) -> Mission:
    mission = db.query(Mission).filter(Mission.id == mission_id, Mission.is_active.is_(True)).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Миссия не найдена")
    return mission


@router.get("/{mission_id}", response_model=PythonMissionState)
def mission_state(
    mission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PythonMissionState:
    mission = _get_mission(db, mission_id)
    return build_state(db, current_user, mission)


@router.post("/{mission_id}/submit", response_model=PythonSubmissionRead)
def mission_submit(
    mission_id: int,
    payload: PythonSubmitRequest,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PythonSubmissionRead:
    mission = _get_mission(db, mission_id)
    submission = submit_code(db, current_user, mission, challenge_id=payload.challenge_id, code=payload.code)
    return PythonSubmissionRead.model_validate(submission)
