"""Seed artifacts data."""

from sqlalchemy.orm import Session

from app.models.artifact import Artifact, ArtifactRarity


def seed_artifacts(session: Session) -> list[Artifact]:
    """Create and return artifacts."""
    artifact_specs = [
        {
            "name": "Полотенце №42",
            "description": "Надёжный текстиль, который всегда напоминает не паниковать и держаться курса.",
            "rarity": ArtifactRarity.RARE,
            "image_url": "/artifacts/polotentse-42.jpg",
        },
        {
            "name": "Путеводитель по Галактике",
            "description": "Электронный том, который шепчет полезные подсказки на любом языке Вселенной.",
            "rarity": ArtifactRarity.LEGENDARY,
            "image_url": "/artifacts/putevoditel-galaktiki.jpg",
        },
        {
            "name": "Пангалактический грызлодёр",
            "description": "Термос с рецептом самого невероятного коктейля во Вселенной.",
            "rarity": ArtifactRarity.EPIC,
            "image_url": "/artifacts/pangalakticheskiy-gryzloder.jpg",
        },
        {
            "name": "Бабель-рыбка",
            "description": "Маленький переводчик, который делает любые брифинги понятными.",
            "rarity": ArtifactRarity.EPIC,
            "image_url": "/artifacts/babel-rybka.jpg",
        },
        {
            "name": "Карандаш Слаартибартфаста",
            "description": "Инструмент планетарного дизайна для тех, кто чертит новые траектории.",
            "rarity": ArtifactRarity.COMMON,
            "image_url": "/artifacts/karandash-slaartibartfasta.jpg",
        },
        {
            "name": "Кнопка невероятности",
            "description": "Ламинарный кристалл, который слегка смещает вероятность в вашу пользу.",
            "rarity": ArtifactRarity.LEGENDARY,
            "image_url": "/artifacts/knopka-neveroyatnosti.jpg",
        },
        {
            "name": "Чай из станции Магратеи",
            "description": "Колба с идеальным напитком, который стабилизирует мораль экипажа.",
            "rarity": ArtifactRarity.RARE,
            "image_url": "/artifacts/chai-magratea.jpg",
        },
        {
            "name": "Сфера воодушевления Марвина",
            "description": "Мягкий светящийся куб, повышающий уровень эмпатии на борту.",
            "rarity": ArtifactRarity.COMMON,
            "image_url": "/artifacts/sfera-marvina.jpg",
        },
        {
            "name": "Компас невероятности",
            "description": "Эталонная стрелка, показывающая самый выгодный вариант во множестве вероятностей.",
            "rarity": ArtifactRarity.RARE,
            "image_url": "/artifacts/kompas-neveroyatnosti.jpg",
        },
        {
            "name": "Голографический пингвин Эдди",
            "description": "Проекционный талисман, который поддерживает мораль экипажа шутками.",
            "rarity": ArtifactRarity.COMMON,
            "image_url": "/artifacts/golograficheskiy-pingvin-eddie.jpg",
        },
    ]
    artifacts = [Artifact(**spec) for spec in artifact_specs]
    session.add_all(artifacts)
    session.flush()
    return artifacts
