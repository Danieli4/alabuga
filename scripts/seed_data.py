"""Наполнение демонстрационными данными."""

from __future__ import annotations

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
from app.models.mission import Mission, MissionCompetencyReward, MissionDifficulty, MissionFormat
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.onboarding import OnboardingSlide
from app.models.store import StoreItem
from app.models.python import PythonChallenge
from app.models.user import Competency, CompetencyCategory, User, UserCompetency, UserRole, UserArtifact
from app.models.journal import JournalEntry, JournalEventType
from app.main import run_migrations

DATA_SENTINEL = settings.sqlite_path.parent / ".seeded"


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
            description="Живые встречи в кампусе и городе",
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
        mission_campus_tour = Mission(
            title="Экскурсия по кампусу",
            description="Познакомьтесь с производственными линиями и учебными площадками вместе с наставником.",
            xp_reward=140,
            mana_reward=70,
            difficulty=MissionDifficulty.EASY,
            format=MissionFormat.OFFLINE,
            event_location="Кампус Алабуга Политех",
            event_address="Республика Татарстан, Елабуга, территория ОЭЗ 'Алабуга'",
            event_starts_at=now + timedelta(days=3, hours=10),
            event_ends_at=now + timedelta(days=3, hours=13),
            registration_deadline=now + timedelta(days=2, hours=18),
            capacity=25,
            contact_person="Наталья из HR",
            contact_phone="+7 (900) 123-45-67",
            registration_notes="Возьмите паспорт для прохода на территорию.",
        )
        mission_sport_day = Mission(
            title="Спортивный день в технопарке",
            description="Присоединяйтесь к командным активностям и познакомьтесь с будущими коллегами в неформальной обстановке.",
            xp_reward=160,
            mana_reward=90,
            difficulty=MissionDifficulty.MEDIUM,
            format=MissionFormat.OFFLINE,
            event_location="Спортивный центр Алабуги",
            event_address="Елабуга, проспект Строителей, 5",
            event_starts_at=now + timedelta(days=7, hours=17),
            event_ends_at=now + timedelta(days=7, hours=20),
            registration_deadline=now + timedelta(days=6, hours=12),
            capacity=40,
            contact_person="Игорь, координатор мероприятий",
            contact_phone="+7 (900) 765-43-21",
            registration_notes="Форма одежды – спортивная. Будет организован трансфер от кампуса.",
        )
        mission_open_lecture = Mission(
            title="Лекция капитана по культуре Алабуги",
            description="Живой рассказ о миссии компании, ценностях и истории от капитана программы.",
            xp_reward=180,
            mana_reward=110,
            difficulty=MissionDifficulty.MEDIUM,
            format=MissionFormat.OFFLINE,
            event_location="Конференц-зал HQ",
            event_address="Елабуга, ул. Промышленная, 2",
            event_starts_at=now + timedelta(days=10, hours=15),
            event_ends_at=now + timedelta(days=10, hours=17),
            registration_deadline=now + timedelta(days=8, hours=18),
            capacity=60,
            contact_person="Алина, программа адаптации",
            contact_phone="+7 (900) 555-19-82",
            registration_notes="Перед лекцией будет кофе-брейк, приходите на 15 минут раньше.",
        )
        session.add_all([
            mission_documents,
            mission_resume,
            mission_interview,
            mission_onboarding,
            mission_python_basics,
            mission_campus_tour,
            mission_sport_day,
            mission_open_lecture,
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
                    mission_id=mission_campus_tour.id,
                    competency_id=competencies[0].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_sport_day.id,
                    competency_id=competencies[3].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_open_lecture.id,
                    competency_id=competencies[5].id,
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
                BranchMission(branch_id=offline_branch.id, mission_id=mission_campus_tour.id, order=1),
                BranchMission(branch_id=offline_branch.id, mission_id=mission_sport_day.id, order=2),
                BranchMission(branch_id=offline_branch.id, mission_id=mission_open_lecture.id, order=3),
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
