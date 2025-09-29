"""Запуск пользовательского Python-кода в отдельном процессе."""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
import sys
from typing import Final


DEFAULT_TIMEOUT_SECONDS: Final[float] = 5.0


@dataclass(slots=True)
class PythonRunResult:
    """Результат выполнения пользовательской программы."""

    stdout: str
    stderr: str
    exit_code: int
    timeout: bool = False


def run_user_python_code(code: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> PythonRunResult:
    """Запускаем код в отдельном процессе и возвращаем stdout/stderr.

    Код выполняется через ``sys.executable`` в режиме ``-c``. Таймаут ограничен,
    чтобы бесконечные циклы не блокировали API. Любые ошибки компиляции или
    выполнения попадают в ``stderr`` и возвращаются пользователю без изменений.
    """

    try:
        completed = subprocess.run(  # noqa: PLW1510 - таймаут обрабатываем вручную
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stderr = exc.stderr or ""
        if stderr:
            stderr = f"{stderr}\nПрограмма превысила лимит {timeout:.1f} сек."
        else:
            stderr = f"Программа превысила лимит {timeout:.1f} сек."
        return PythonRunResult(stdout=exc.stdout or "", stderr=stderr, exit_code=124, timeout=True)

    return PythonRunResult(
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
        timeout=False,
    )

