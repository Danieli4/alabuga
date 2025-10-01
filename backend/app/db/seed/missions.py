"""Seed missions data."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.branch import Branch, BranchMission
from app.models.coding import CodingChallenge
from app.models.mission import Mission, MissionCompetencyReward, MissionDifficulty, MissionFormat
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.user import Competency


def seed_missions(
    session: Session,
    branches: dict[str, Branch],
    ranks: list[Rank],
    artifacts: list[Artifact],
    competencies: list[Competency],
) -> dict[str, Mission]:
    """Create and return missions with all related data."""
    artifact_by_name = {artifact.name: artifact for artifact in artifacts}
    
    # Main quest missions
    mission_documents = Mission(
        title="Загрузка документов",
        description="Соберите полный пакет документов для HR",
        xp_reward=100,
        mana_reward=50,
        difficulty=MissionDifficulty.EASY,
        minimum_rank_id=ranks[0].id,
        artifact_id=artifact_by_name["Путеводитель по Галактике"].id,
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
        artifact_id=artifact_by_name["Полотенце №42"].id,
    )
    mission_onboarding = Mission(
        title="Онбординг экипажа",
        description="Познакомьтесь с кораблём и командой",
        xp_reward=200,
        mana_reward=100,
        difficulty=MissionDifficulty.HARD,
        minimum_rank_id=ranks[1].id,
    )
    
    # Python training mission
    mission_python_basics = Mission(
        title="Основные знания Python",
        description="Решите 10 небольших задач и докажите, что уверенно чувствуете себя в языке программирования.",
        xp_reward=250,
        mana_reward=120,
        difficulty=MissionDifficulty.MEDIUM,
        minimum_rank_id=ranks[0].id,
    )
    
    # Offline event missions
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
    
    # Add competency rewards
    session.add_all([
        MissionCompetencyReward(
            mission_id=mission_documents.id,
            competency_id=competencies[1].id,  # Коммуникация
            level_delta=1,
        ),
        MissionCompetencyReward(
            mission_id=mission_resume.id,
            competency_id=competencies[0].id,  # Навигация
            level_delta=1,
        ),
        MissionCompetencyReward(
            mission_id=mission_interview.id,
            competency_id=competencies[1].id,  # Коммуникация
            level_delta=1,
        ),
        MissionCompetencyReward(
            mission_id=mission_onboarding.id,
            competency_id=competencies[3].id,  # Командная работа
            level_delta=1,
        ),
        MissionCompetencyReward(
            mission_id=mission_python_basics.id,
            competency_id=competencies[2].id,  # Инженерия
            level_delta=1,
        ),
        MissionCompetencyReward(
            mission_id=mission_campus_tour.id,
            competency_id=competencies[0].id,  # Навигация
            level_delta=1,
        ),
        MissionCompetencyReward(
            mission_id=mission_sport_day.id,
            competency_id=competencies[3].id,  # Командная работа
            level_delta=1,
        ),
        MissionCompetencyReward(
            mission_id=mission_open_lecture.id,
            competency_id=competencies[5].id,  # Культура
            level_delta=1,
        ),
    ])
    
    # Link missions to branches
    session.add_all([
        BranchMission(branch_id=branches["main"].id, mission_id=mission_documents.id, order=1),
        BranchMission(branch_id=branches["main"].id, mission_id=mission_resume.id, order=2),
        BranchMission(branch_id=branches["main"].id, mission_id=mission_interview.id, order=3),
        BranchMission(branch_id=branches["main"].id, mission_id=mission_onboarding.id, order=4),
        BranchMission(branch_id=branches["python"].id, mission_id=mission_python_basics.id, order=1),
        BranchMission(branch_id=branches["offline"].id, mission_id=mission_campus_tour.id, order=1),
        BranchMission(branch_id=branches["offline"].id, mission_id=mission_sport_day.id, order=2),
        BranchMission(branch_id=branches["offline"].id, mission_id=mission_open_lecture.id, order=3),
    ])
    
    # Add Python challenges
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
    
    session.add_all([
        CodingChallenge(
            mission_id=mission_python_basics.id,
            order=spec["order"],
            title=spec["title"],
            prompt=spec["prompt"],
            starter_code=spec["starter_code"],
            expected_output=spec["expected_output"],
        )
        for spec in python_challenges_specs
    ])
    
    # Add rank requirements
    session.add_all([
        RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_documents.id),
        RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_resume.id),
        RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_interview.id),
        RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_onboarding.id),
        RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_python_basics.id),
    ])
    
    session.add_all([
        RankCompetencyRequirement(
            rank_id=ranks[1].id,
            competency_id=competencies[1].id,  # Коммуникация
            required_level=1,
        ),
        RankCompetencyRequirement(
            rank_id=ranks[2].id,
            competency_id=competencies[3].id,  # Командная работа
            required_level=1,
        ),
    ])
    
    return {
        "documents": mission_documents,
        "resume": mission_resume,
        "interview": mission_interview,
        "onboarding": mission_onboarding,
        "python_basics": mission_python_basics,
        "campus_tour": mission_campus_tour,
        "sport_day": mission_sport_day,
        "open_lecture": mission_open_lecture,
    }
