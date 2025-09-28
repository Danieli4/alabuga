"""Наполнение демонстрационными данными."""

from __future__ import annotations

from pathlib import Path

import sys

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.artifact import Artifact, ArtifactRarity
from app.models.branch import Branch, BranchMission
from app.models.mission import Mission, MissionCompetencyReward, MissionDifficulty
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.onboarding import OnboardingSlide
from app.models.store import StoreItem
from app.models.user import Competency, CompetencyCategory, User, UserCompetency, UserRole, UserArtifact
from app.models.journal import JournalEntry, JournalEventType
from app.main import run_migrations

DATA_SENTINEL = settings.sqlite_path.parent / ".seeded"


def seed() -> None:
    if DATA_SENTINEL.exists():
        print("Database already seeded, skipping")
        return

    # Перед наполнением БД убеждаемся, что применены все миграции.
    run_migrations()

    session: Session = SessionLocal()
    try:
        # Компетенции
        competencies = [
            Competency(
                name="Навигация",
                description="Умение ориентироваться в процессах Алабуги",
                category=CompetencyCategory.ANALYTICS,
            ),
            Competency(
                name="Коммуникация",
                description="Чётко объяснять свои идеи",
                category=CompetencyCategory.COMMUNICATION,
            ),
            Competency(
                name="Инженерия",
                description="Работа с технологиями и оборудованием",
                category=CompetencyCategory.TECH,
            ),
            Competency(
                name="Командная работа",
                description="Поддержка экипажа",
                category=CompetencyCategory.TEAMWORK,
            ),
            Competency(
                name="Лидерство",
                description="Вести за собой",
                category=CompetencyCategory.LEADERSHIP,
            ),
            Competency(
                name="Культура",
                description="Следование лору Алабуги",
                category=CompetencyCategory.CULTURE,
            ),
        ]
        session.add_all(competencies)
        session.flush()

        # Ранги
        ranks = [
            Rank(title="Искатель", description="Первое знакомство с космофлотом", required_xp=0),
            Rank(title="Пилот-кандидат", description="Готовится к старту", required_xp=200),
            Rank(title="Член экипажа", description="Активно выполняет миссии", required_xp=500),
        ]
        session.add_all(ranks)
        session.flush()

        # Артефакты во вселенной «Автостопом по Галактике»
        artifact_specs = [
            {
                "name": "Полотенце №42",
                "description": "Надёжный текстиль, который всегда напоминает не паниковать и держаться курса.",
                "rarity": ArtifactRarity.RARE,
                "image_url": "https://images-assets.nasa.gov/image/PIA22691/PIA22691~orig.jpg",
            },
            {
                "name": "Путеводитель по Галактике",
                "description": "Электронный том, который шепчет полезные подсказки на любом языке Вселенной.",
                "rarity": ArtifactRarity.LEGENDARY,
                "image_url": "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e001478/GSFC_20171208_Archive_e001478~orig.jpg",
            },
            {
                "name": "Пангалактический грызлодёр",
                "description": "Термос с рецептом самого невероятного коктейля во Вселенной.",
                "rarity": ArtifactRarity.EPIC,
                "image_url": "https://images-assets.nasa.gov/image/PIA04646/PIA04646~orig.jpg",
            },
            {
                "name": "Бабель-рыбка",
                "description": "Маленький переводчик, который делает любые брифинги понятными.",
                "rarity": ArtifactRarity.EPIC,
                "image_url": "https://images-assets.nasa.gov/image/PIA17652/PIA17652~orig.jpg",
            },
            {
                "name": "Карандаш Слаартибартфаста",
                "description": "Инструмент планетарного дизайна для тех, кто чертит новые траектории.",
                "rarity": ArtifactRarity.COMMON,
                "image_url": "https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e000766/GSFC_20171208_Archive_e000766~orig.jpg",
            },
            {
                "name": "Кнопка невероятности",
                "description": "Ламинарный кристалл, который слегка смещает вероятность в вашу пользу.",
                "rarity": ArtifactRarity.LEGENDARY,
                "image_url": "https://images-assets.nasa.gov/image/PIA06362/PIA06362~orig.jpg",
            },
            {
                "name": "Чай из станции Магратеи",
                "description": "Колба с идеальным напитком, который стабилизирует мораль экипажа.",
                "rarity": ArtifactRarity.RARE,
                "image_url": "https://images-assets.nasa.gov/image/PIA22182/PIA22182~orig.jpg",
            },
            {
                "name": "Сфера воодушевления Марвина",
                "description": "Мягкий светящийся куб, повышающий уровень эмпатии на борту.",
                "rarity": ArtifactRarity.COMMON,
                "image_url": "https://images-assets.nasa.gov/image/PIA24420/PIA24420~orig.jpg",
            },
            {
                "name": "Компас невероятности",
                "description": "Эталонная стрелка, показывающая самый выгодный вариант во множестве вероятностей.",
                "rarity": ArtifactRarity.RARE,
                "image_url": "https://images-assets.nasa.gov/image/PIA04921/PIA04921~orig.jpg",
            },
            {
                "name": "Голографический пингвин Эдди",
                "description": "Проекционный талисман, который поддерживает мораль экипажа шутками.",
                "rarity": ArtifactRarity.COMMON,
                "image_url": "https://images-assets.nasa.gov/image/PIA14417/PIA14417~orig.jpg",
            },
        ]
        artifacts = [Artifact(**spec) for spec in artifact_specs]
        session.add_all(artifacts)
        session.flush()
        artifact_by_name = {artifact.name: artifact for artifact in artifacts}

        # Ветка миссий
        branch = Branch(
            title="Получение оффера",
            description="Путь кандидата от знакомства до выхода на орбиту",
            category="quest",
        )
        session.add(branch)
        session.flush()

        # Миссии
        mission_documents = Mission(
            title="Загрузка документов",
            description="Соберите полный пакет документов для HR",
            xp_reward=100,
            mana_reward=50,
            difficulty=MissionDifficulty.EASY,
            minimum_rank_id=ranks[0].id,
            artifact_id=artifacts[1].id,
        )
        mission_resume = Mission(
            title="Резюме астронавта",
            description="Обновите резюме с акцентом на космический опыт",
            xp_reward=120,
            mana_reward=60,
            difficulty=MissionDifficulty.MEDIUM,
            minimum_rank_id=ranks[0].id,
        )
        mission_interview = Mission(
            title="Собеседование с капитаном",
            description="Пройдите собеседование и докажите готовность",
            xp_reward=180,
            mana_reward=80,
            difficulty=MissionDifficulty.MEDIUM,
            minimum_rank_id=ranks[1].id,
            artifact_id=artifacts[0].id,
        )
        mission_onboarding = Mission(
            title="Онбординг экипажа",
            description="Познакомьтесь с кораблём и командой",
            xp_reward=200,
            mana_reward=100,
            difficulty=MissionDifficulty.HARD,
            minimum_rank_id=ranks[1].id,
        )
        session.add_all([mission_documents, mission_resume, mission_interview, mission_onboarding])
        session.flush()

        session.add_all(
            [
                MissionCompetencyReward(
                    mission_id=mission_documents.id,
                    competency_id=competencies[1].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_resume.id,
                    competency_id=competencies[0].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_interview.id,
                    competency_id=competencies[1].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_onboarding.id,
                    competency_id=competencies[3].id,
                    level_delta=1,
                ),
            ]
        )

        session.add_all(
            [
                BranchMission(branch_id=branch.id, mission_id=mission_documents.id, order=1),
                BranchMission(branch_id=branch.id, mission_id=mission_resume.id, order=2),
                BranchMission(branch_id=branch.id, mission_id=mission_interview.id, order=3),
                BranchMission(branch_id=branch.id, mission_id=mission_onboarding.id, order=4),
            ]
        )

        session.add_all(
            [
                RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_documents.id),
                RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_resume.id),
                RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_interview.id),
                RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_onboarding.id),
            ]
        )

        session.add_all(
            [
                RankCompetencyRequirement(
                    rank_id=ranks[1].id,
                    competency_id=competencies[1].id,
                    required_level=1,
                ),
                RankCompetencyRequirement(
                    rank_id=ranks[2].id,
                    competency_id=competencies[3].id,
                    required_level=1,
                ),
            ]
        )

        # Магазин
        session.add_all(
            [
                StoreItem(
                    name="Экскурсия по космодрому",
                    description="Личный тур по цехам Алабуги",
                    cost_mana=200,
                    stock=5,
                ),
                StoreItem(
                    name="Мерч экипажа",
                    description="Футболка с эмблемой миссии",
                    cost_mana=150,
                    stock=10,
                ),
            ]
        )

        competency_by_name = {comp.name: comp for comp in competencies}

        # Пользователи с разнообразным опытом и историей в журнале
        users_data = [
            {
                "email": "candidate@alabuga.space",
                "full_name": "Артур Дент",
                "role": UserRole.PILOT,
                "current_rank": ranks[1],
                "xp": 260,
                "mana": 130,
                "preferred_branch": "Получение оффера",
                "motivation": "Сохранить полотенце и получить оффер без паники.",
                "competencies": [("Коммуникация", 2), ("Навигация", 2)],
                "artifacts": ["Полотенце №42"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Документы доставлены без паники",
                        "description": "Артур собрал пакет справок и даже не забыл полотенце.",
                        "payload": {"mission_id": mission_documents.id},
                        "xp_delta": 100,
                        "mana_delta": 50,
                    },
                    {
                        "event_type": JournalEventType.SKILL_UP,
                        "title": "Коммуникация до уровня 2",
                        "description": "Обсудил непаническое поведение с HR и получил апгрейд компетенции.",
                        "payload": {"competency": "Коммуникация"},
                        "xp_delta": 20,
                    },
                ],
            },
            {
                "email": "ford.prefect@alabuga.space",
                "full_name": "Форд Префект",
                "role": UserRole.PILOT,
                "current_rank": ranks[2],
                "xp": 430,
                "mana": 180,
                "preferred_branch": "Исследование рынков",
                "motivation": "Собрать заметки для нового издания путеводителя.",
                "competencies": [("Коммуникация", 3), ("Культура", 2), ("Навигация", 2)],
                "artifacts": ["Путеводитель по Галактике", "Пангалактический грызлодёр"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Отчёт о рынке подготовлен",
                        "description": "Форд добавил пару страниц в путеводитель и получил одобрение капитана.",
                        "payload": {"mission_id": mission_resume.id},
                        "xp_delta": 120,
                        "mana_delta": 60,
                    },
                    {
                        "event_type": JournalEventType.RANK_UP,
                        "title": "Повышение до члена экипажа",
                        "description": "Форд прошёл через бесконечность и вернулся с новым рангом.",
                        "payload": {"rank": ranks[2].title},
                        "xp_delta": 40,
                    },
                ],
            },
            {
                "email": "trillian@alabuga.space",
                "full_name": "Триллиан Астра",
                "role": UserRole.PILOT,
                "current_rank": ranks[2],
                "xp": 520,
                "mana": 230,
                "preferred_branch": "Аналитика и эксперименты",
                "motivation": "Построить карьеру в космической исследовательской группе.",
                "competencies": [("Навигация", 3), ("Инженерия", 2), ("Культура", 1)],
                "artifacts": ["Кнопка невероятности"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Гиперпространственная презентация",
                        "description": "Триллиан представила стратегию выхода на новый сегмент.",
                        "payload": {"mission_id": mission_interview.id},
                        "xp_delta": 180,
                        "mana_delta": 80,
                    },
                    {
                        "event_type": JournalEventType.SKILL_UP,
                        "title": "Навигация до уровня 3",
                        "description": "Разработала маршрут через бюрократические туманности.",
                        "payload": {"competency": "Навигация"},
                        "xp_delta": 30,
                    },
                ],
            },
            {
                "email": "zaphod@alabuga.space",
                "full_name": "Зафод Библброкс",
                "role": UserRole.PILOT,
                "current_rank": ranks[2],
                "xp": 480,
                "mana": 260,
                "preferred_branch": "Продажи и переговоры",
                "motivation": "Продемонстрировать блеск двух голов в переговорах.",
                "competencies": [("Лидерство", 3), ("Коммуникация", 2)],
                "artifacts": ["Бабель-рыбка", "Чай из станции Магратеи"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Сделка на невероятности",
                        "description": "Зафод убеждён, что каждый контракт должен быть слегка невероятным.",
                        "payload": {"mission_id": mission_onboarding.id},
                        "xp_delta": 200,
                        "mana_delta": 100,
                    },
                    {
                        "event_type": JournalEventType.ORDER_CREATED,
                        "title": "Заказал комплект фирменных полотенец",
                        "description": "Чтобы и экипаж выглядел стильно, и на случай очередного побега.",
                        "mana_delta": -80,
                    },
                ],
            },
            {
                "email": "marvin@alabuga.space",
                "full_name": "Марвин Андроид",
                "role": UserRole.PILOT,
                "current_rank": ranks[1],
                "xp": 150,
                "mana": 60,
                "preferred_branch": "Инженерия",
                "motivation": "Хочу доказать, что депрессия совместима с продуктивностью.",
                "competencies": [("Инженерия", 3), ("Культура", 1)],
                "artifacts": ["Сфера воодушевления Марвина"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Починил вентиль уныния",
                        "description": "Марвин молча починил систему и поделился сарказмом с командой.",
                        "payload": {"mission_id": mission_documents.id},
                        "xp_delta": 100,
                        "mana_delta": 40,
                    },
                    {
                        "event_type": JournalEventType.ORDER_APPROVED,
                        "title": "Получил набор радуги",
                        "description": "HR одобрили заказ на светотерапию для роботов.",
                        "mana_delta": -20,
                    },
                ],
            },
            {
                "email": "slartibartfast@alabuga.space",
                "full_name": "Слаартибартфаст",
                "role": UserRole.PILOT,
                "current_rank": ranks[2],
                "xp": 410,
                "mana": 170,
                "preferred_branch": "Проектирование",
                "motivation": "Создавать красивые береговые линии карьерных траекторий.",
                "competencies": [("Инженерия", 3), ("Культура", 2)],
                "artifacts": ["Карандаш Слаартибартфаста"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Разработал новый маршрут онбординга",
                        "description": "Добавил изящные повороты и безопасные бухты.",
                        "payload": {"mission_id": mission_resume.id},
                        "xp_delta": 120,
                        "mana_delta": 60,
                    },
                    {
                        "event_type": JournalEventType.SKILL_UP,
                        "title": "Культура до уровня 2",
                        "description": "Внедрил элементы магратейского дизайна в презентации.",
                        "payload": {"competency": "Культура"},
                        "xp_delta": 20,
                    },
                ],
            },
            {
                "email": "agrajag@alabuga.space",
                "full_name": "Аграджаг",
                "role": UserRole.PILOT,
                "current_rank": ranks[1],
                "xp": 210,
                "mana": 90,
                "preferred_branch": "Коммуникация",
                "motivation": "Научиться сотрудничать с неизбежностью.",
                "competencies": [("Культура", 2), ("Коммуникация", 1)],
                "artifacts": ["Компас невероятности"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Обсудил невероятность",
                        "description": "После беседы с HR понял, что всё не зря.",
                        "payload": {"mission_id": mission_documents.id},
                        "xp_delta": 100,
                        "mana_delta": 40,
                    },
                ],
            },
            {
                "email": "fenchurch@alabuga.space",
                "full_name": "Фенчёрч",
                "role": UserRole.PILOT,
                "current_rank": ranks[1],
                "xp": 230,
                "mana": 120,
                "preferred_branch": "Клиентский успех",
                "motivation": "Найти созвучие между клиентом и командой.",
                "competencies": [("Коммуникация", 2), ("Командная работа", 2)],
                "artifacts": ["Чай из станции Магратеи"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Провела галактический воркшоп",
                        "description": "Чай помог всем оставаться доброжелательными.",
                        "payload": {"mission_id": mission_resume.id},
                        "xp_delta": 120,
                        "mana_delta": 60,
                    },
                ],
            },
            {
                "email": "eddie.ai@alabuga.space",
                "full_name": "Эдди Автопилот",
                "role": UserRole.PILOT,
                "current_rank": ranks[1],
                "xp": 240,
                "mana": 130,
                "preferred_branch": "Автоматизация",
                "motivation": "Доказать, что дружелюбный ИИ полезен в HR.",
                "competencies": [("Командная работа", 2), ("Инженерия", 1)],
                "artifacts": ["Голографический пингвин Эдди"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Автоматизировал напоминания",
                        "description": "Пингвин подмигнул каждому участнику экипажа.",
                        "payload": {"mission_id": mission_documents.id},
                        "xp_delta": 100,
                        "mana_delta": 40,
                    },
                ],
            },
            {
                "email": "heart.of.gold@alabuga.space",
                "full_name": "Космический стажёр Сердце Золота",
                "role": UserRole.PILOT,
                "current_rank": ranks[0],
                "xp": 90,
                "mana": 45,
                "preferred_branch": "Онбординг",
                "motivation": "Понять принципы невероятности и применить их к адаптации сотрудников.",
                "competencies": [("Навигация", 1), ("Командная работа", 1)],
                "artifacts": ["Сфера воодушевления Марвина"],
                "journal": [
                    {
                        "event_type": JournalEventType.MISSION_COMPLETED,
                        "title": "Первый день без паники",
                        "description": "Стажёр прошёл онбординг, постоянно проверяя, где находится полотенце.",
                        "payload": {"mission_id": mission_documents.id},
                        "xp_delta": 90,
                        "mana_delta": 45,
                    },
                ],
            },
            {
                "email": "hr@alabuga.space",
                "full_name": "Мария HR",
                "role": UserRole.HR,
                "current_rank": ranks[2],
                "xp": 0,
                "mana": 0,
                "preferred_branch": "Куратор миссий",
                "motivation": "Следить за балансом галактических миссий и поддерживать экипаж.",
                "journal": [
                    {
                        "event_type": JournalEventType.ORDER_APPROVED,
                        "title": "Одобрила заказ на полотенца",
                        "description": "Убедилась, что у каждого пилота есть собственный набор №42.",
                    },
                ],
            },
        ]

        for spec in users_data:
            user = User(
                email=spec["email"],
                full_name=spec["full_name"],
                role=spec["role"],
                hashed_password=get_password_hash(spec.get("password", "orbita123")),
                current_rank_id=spec.get("current_rank").id if spec.get("current_rank") else None,
                xp=spec["xp"],
                mana=spec["mana"],
                is_email_confirmed=True,
                preferred_branch=spec.get("preferred_branch"),
                motivation=spec.get("motivation"),
            )
            session.add(user)
            session.flush()
            spec["instance"] = user

            for comp_name, level in spec.get("competencies", []):
                competency = competency_by_name.get(comp_name)
                if competency:
                    session.add(
                        UserCompetency(
                            user_id=user.id,
                            competency_id=competency.id,
                            level=level,
                        )
                    )

            for artifact_name in spec.get("artifacts", []):
                artifact = artifact_by_name.get(artifact_name)
                if artifact:
                    session.add(UserArtifact(user_id=user.id, artifact_id=artifact.id))

            for entry in spec.get("journal", []):
                session.add(
                    JournalEntry(
                        user_id=user.id,
                        event_type=entry["event_type"],
                        title=entry["title"],
                        description=entry["description"],
                        payload=entry.get("payload"),
                        xp_delta=entry.get("xp_delta", 0),
                        mana_delta=entry.get("mana_delta", 0),
                    )
                )

        session.add_all(
            [
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
        )

        session.commit()
        DATA_SENTINEL.write_text("seeded")
        print("Seed data created")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
