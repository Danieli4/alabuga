"""Seed onboarding slides data."""

from sqlalchemy.orm import Session

from app.models.onboarding import OnboardingSlide


def seed_onboarding_slides(session: Session) -> list[OnboardingSlide]:
    """Create and return onboarding slides."""
    slides = [
        OnboardingSlide(
            order=1,
            title="Добро пожаловать в орбитальный флот",
            body="Узнайте, как миссии помогают связать карьерные шаги в единую траекторию.",
            media_url="https://images.nasa.gov/details-PIA12235",
            cta_text="Перейти к миссиям",
            cta_link="/missions",
        ),
        OnboardingSlide(
            order=2,
            title="Получайте опыт и ману",
            body="Выполняя задания, вы накапливаете опыт для повышения ранга и ману для магазина.",
            media_url="https://images.nasa.gov/details-PIA23499",
        ),
        OnboardingSlide(
            order=3,
            title="Повышайте ранг до члена экипажа",
            body="Закройте ключевые миссии ветки «Получение оффера» и прокачайте компетенции.",
            cta_text="Открыть ветку",
            cta_link="/missions",
        ),
    ]
    session.add_all(slides)
    session.flush()
    return slides
