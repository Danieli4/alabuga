"""Наполнение демонстрационными данными."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import sys

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.artifact import Artifact, ArtifactRarity
from app.models.branch import Branch, BranchMission
from app.models.coding import CodingChallenge
from app.models.mission import (
    Mission,
    MissionCompetencyReward,
    MissionDifficulty,
    MissionFormat,
)
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.onboarding import OnboardingSlide
from app.models.store import StoreItem
from app.models.python import PythonChallenge
from app.models.user import Competency, CompetencyCategory, User, UserCompetency, UserRole, UserArtifact
from app.models.journal import JournalEntry, JournalEventType
from app.main import run_migrations

DATA_SENTINEL = settings.sqlite_path.parent / ".seeded"


EXCURSION_IMAGE_B64 = (
    "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"
    "RU5ErkJggg=="
)


MERCH_IMAGE_B64 = (
    "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"
    "RK5CYII="
)


def ensure_store_image(filename: str, encoded: str) -> str:
    """Создаём файл изображения в uploads/store и возвращаем относительный путь."""

    target = settings.uploads_path / "store" / filename
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(encoded))
    return target.relative_to(settings.uploads_path).as_posix()


def seed() -> None:
    if DATA_SENTINEL.exists():
        print("Database already seeded, skipping")
        return

    # Перед наполнением БД убеждаемся, что применены все миграции.
    original_cwd = Path.cwd()
    try:
        os.chdir(ROOT / 'backend')
        run_migrations()
    finally:
        os.chdir(original_cwd)

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
        artifact_by_name = {artifact.name: artifact for artifact in artifacts}

        # Ветка миссий
        branch = Branch(
            title="Получение оффера",
            description="Путь кандидата от знакомства до выхода на орбиту",
            category="quest",
        )
        python_branch = Branch(
            title="Основы Python",
            description="Мини-курс из 10 задач для проверки синтаксиса и базовой логики.",
            category="training",
        )
        offline_branch = Branch(
            title="Офлайн мероприятия",
            description="Экскурсии, лекции и спортивные сборы, которые помогают прочувствовать атмосферу кампуса.",
            category="event",
        )
        session.add_all([branch, python_branch, offline_branch])
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
        mission_python_basics = Mission(
            title="Основные знания Python",
            description="Решите 10 небольших задач и докажите, что уверенно чувствуете себя в языке программирования.",
            xp_reward=250,
            mana_reward=120,
            difficulty=MissionDifficulty.MEDIUM,
            minimum_rank_id=ranks[0].id,
        )
        now = datetime.now(timezone.utc)
        mission_excursion = Mission(
            title="Экскурсия по кампусу",
            description="Очное знакомство с производством и инженерными лабораториями Алабуги.",
            xp_reward=80,
            mana_reward=40,
            difficulty=MissionDifficulty.EASY,
            format=MissionFormat.OFFLINE,
            minimum_rank_id=ranks[0].id,
            registration_deadline=now + timedelta(days=2, hours=18),
            starts_at=now + timedelta(days=3, hours=10),
            ends_at=now + timedelta(days=3, hours=12),
            location_title="Точка сбора в холле «Орбита»",
            location_address="Республика Татарстан, Елабужский район, территория ОЭЗ «Алабуга»",
            location_url="https://yandex.ru/maps/-/CDuA5Jm0",
            capacity=25,
        )
        mission_lecture = Mission(
            title="Лекция «Будущее инженерных профессий»",
            description="Закрытая офлайн-сессия с руководителями направлений и сессией вопросов-ответов.",
            xp_reward=120,
            mana_reward=60,
            difficulty=MissionDifficulty.MEDIUM,
            format=MissionFormat.OFFLINE,
            minimum_rank_id=ranks[0].id,
            registration_deadline=now + timedelta(days=5),
            starts_at=now + timedelta(days=6, hours=17),
            ends_at=now + timedelta(days=6, hours=19),
            location_title="Амфитеатр технопарка",
            location_address="Корпус «Новые технологии», 2 этаж",
            location_url="https://yandex.ru/maps/-/CDuA5IKU",
            capacity=60,
        )
        mission_sport = Mission(
            title="Утренняя пробежка экипажа",
            description="Лёгкая тренировка и нетворкинг с наставниками перед рабочим днём.",
            xp_reward=90,
            mana_reward=50,
            difficulty=MissionDifficulty.EASY,
            format=MissionFormat.OFFLINE,
            minimum_rank_id=ranks[0].id,
            registration_deadline=now + timedelta(days=1, hours=20),
            starts_at=now + timedelta(days=2, hours=7),
            ends_at=now + timedelta(days=2, hours=8, minutes=30),
            location_title="Беговая дорожка возле корпуса «Космодром»",
            location_address="Променад вокруг учебного центра",
            location_url="https://yandex.ru/maps/-/CDuA5Y1n",
            capacity=30,
        )
        session.add_all([
            mission_documents,
            mission_resume,
            mission_interview,
            mission_onboarding,
            mission_python_basics,
            mission_excursion,
            mission_lecture,
            mission_sport,
        ])
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
                MissionCompetencyReward(
                    mission_id=mission_python_basics.id,
                    competency_id=competencies[2].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_excursion.id,
                    competency_id=competencies[5].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_lecture.id,
                    competency_id=competencies[0].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_sport.id,
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
                BranchMission(branch_id=python_branch.id, mission_id=mission_python_basics.id, order=1),
                BranchMission(branch_id=offline_branch.id, mission_id=mission_excursion.id, order=1),
                BranchMission(branch_id=offline_branch.id, mission_id=mission_sport.id, order=2),
                BranchMission(branch_id=offline_branch.id, mission_id=mission_lecture.id, order=3),
            ]
        )

        python_challenges_specs = [
            {
                "order": 1,
                "title": "Приветствие пилота",
                "prompt": "Выведите в консоль точную фразу «Привет, Python!». Без дополнительных символов или пробелов.",
                "starter_code": "# Напишите одну строку с функцией print\n",
                "expected_output": "Привет, Python!",
            },
            {
                "order": 2,
                "title": "Сложение топлива",
                "prompt": "Создайте переменные a и b, найдите их сумму и выведите результат в формате «Сумма: 12».",
                "starter_code": "a = 7\nb = 5\n# Напечатайте строку в формате: Сумма: 12\n",
                "expected_output": "Сумма: 12",
            },
            {
                "order": 3,
                "title": "Площадь отсека",
                "prompt": "Перемножьте длину и ширину отсека и выведите строку «Площадь: 24».",
                "starter_code": "length = 8\nwidth = 3\n# Вычислите площадь и выведите результат\n",
                "expected_output": "Площадь: 24",
            },
            {
                "order": 4,
                "title": "Обратный отсчёт",
                "prompt": "С помощью цикла for выведите числа от 1 до 5, каждое на новой строке.",
                "starter_code": "for number in range(1, 6):\n    # Напечатайте текущее число\n    pass\n",
                "expected_output": "1\n2\n3\n4\n5",
            },
            {
                "order": 5,
                "title": "Квадраты сигналов",
                "prompt": "Создайте список квадратов чисел от 1 до 5 и выведите строку «Список квадратов: [1, 4, 9, 16, 25]».",
                "starter_code": "levels = [1, 2, 3, 4, 5]\n# Соберите список квадратов и напечатайте его\n",
                "expected_output": "Список квадратов: [1, 4, 9, 16, 25]",
            },
            {
                "order": 6,
                "title": "Длина сообщения",
                "prompt": "Определите длину строки message и выведите её как «Количество символов: 25».",
                "starter_code": "message = \"Пангалактический экспресс\"\n# Посчитайте длину и выведите результат\n",
                "expected_output": "Количество символов: 25",
            },
            {
                "order": 7,
                "title": "Запасы склада",
                "prompt": "Пройдитесь по словарю storage и выведите информацию в формате «мануал: 3» и «датчик: 5».",
                "starter_code": "storage = {\"мануал\": 3, \"датчик\": 5}\n# Выведите данные из словаря построчно\n",
                "expected_output": "мануал: 3\nдатчик: 5",
            },
            {
                "order": 8,
                "title": "Проверка чётности",
                "prompt": "Для чисел 2 и 7 напечатайте на отдельных строках True, если число чётное, иначе False.",
                "starter_code": "numbers = [2, 7]\nfor number in numbers:\n    # Напечатайте True или False в зависимости от чётности\n    pass\n",
                "expected_output": "True\nFalse",
            },
            {
                "order": 9,
                "title": "Сумма диапазона",
                "prompt": "Посчитайте сумму чисел от 1 до 10 и выведите строку «Сумма от 1 до 10: 55».",
                "starter_code": "total = 0\nfor number in range(1, 11):\n    # Добавляйте число к сумме\n    pass\n# После цикла выведите итог\n",
                "expected_output": "Сумма от 1 до 10: 55",
            },
            {
                "order": 10,
                "title": "Факториал 5",
                "prompt": "Вычислите факториал числа 5 и выведите строку «Факториал 5: 120».",
                "starter_code": "result = 1\nfor number in range(1, 6):\n    # Умножайте result на текущее число\n    pass\n# Выведите итоговое значение\n",
                "expected_output": "Факториал 5: 120",
            },
        ]

        session.add_all(
            [
                CodingChallenge(
                    mission_id=mission_python_basics.id,
                    order=spec["order"],
                    title=spec["title"],
                    prompt=spec["prompt"],
                    starter_code=spec["starter_code"],
                    expected_output=spec["expected_output"],
                )
                for spec in python_challenges_specs
            ]
        )

        session.add_all(
            [
                RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_documents.id),
                RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_resume.id),
                RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_interview.id),
                RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_onboarding.id),
                RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_python_basics.id),
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
        excursion_image = ensure_store_image("excursion.png", EXCURSION_IMAGE_B64)
        merch_image = ensure_store_image("merch.png", MERCH_IMAGE_B64)

        session.add_all(
            [
                StoreItem(
                    name="Экскурсия по космодрому",
                    description="Личный тур по цехам Алабуги",
                    cost_mana=200,
                    stock=5,
                    image_url=excursion_image,
                ),
                StoreItem(
                    name="Мерч экипажа",
                    description="Футболка с эмблемой миссии",
                    cost_mana=150,
                    stock=10,
                    image_url=merch_image,
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
