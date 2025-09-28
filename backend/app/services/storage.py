"""Утилиты для сохранения и удаления загруженных файлов."""

from __future__ import annotations

from pathlib import Path
import shutil

from fastapi import UploadFile

from app.core.config import settings


def _ensure_within_base(path: Path) -> None:
    """Проверяем, что путь находится внутри каталога загрузок."""

    base = settings.uploads_path.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(base):
        raise ValueError("Путь выходит за пределы каталога uploads")


def save_submission_document(
    *, upload: UploadFile, user_id: int, mission_id: int, kind: str
) -> str:
    """Сохраняем вложение пользователя и возвращаем относительный путь."""

    extension = Path(upload.filename or "").suffix or ".bin"
    sanitized_extension = extension[:16]

    target_dir = settings.uploads_path / f"user_{user_id}" / f"mission_{mission_id}"
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / f"{kind}{sanitized_extension}"
    with target_path.open("wb") as buffer:
        upload.file.seek(0)
        shutil.copyfileobj(upload.file, buffer)
    upload.file.seek(0)

    relative_path = target_path.relative_to(settings.uploads_path).as_posix()
    return relative_path


def delete_submission_document(relative_path: str | None) -> None:
    """Удаляем файл вложения, если он существует."""

    if not relative_path:
        return

    file_path = settings.uploads_path / relative_path
    try:
        _ensure_within_base(file_path)
    except ValueError:
        return

    if file_path.exists():
        file_path.unlink()
        parent = file_path.parent
        if parent != settings.uploads_path and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
