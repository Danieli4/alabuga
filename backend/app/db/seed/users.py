"""Seed users data."""

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.artifact import Artifact
from app.models.journal import JournalEntry, JournalEventType
from app.models.mission import Mission
from app.models.rank import Rank
from app.models.user import Competency, User, UserArtifact, UserCompetency, UserRole


def seed_users(
    session: Session,
    ranks: list[Rank],
    competencies: list[Competency],
    artifacts: list[Artifact],
    missions: dict[str, Mission],
) -> list[User]:
    """Create and return users with their competencies, artifacts, and journal entries."""
    competency_by_name = {comp.name: comp for comp in competencies}
    artifact_by_name = {artifact.name: artifact for artifact in artifacts}
    
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
                    "payload": {"mission_id": missions["documents"].id},
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
                    "payload": {"mission_id": missions["resume"].id},
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
                    "payload": {"mission_id": missions["interview"].id},
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
                    "payload": {"mission_id": missions["onboarding"].id},
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
                    "payload": {"mission_id": missions["documents"].id},
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
                    "payload": {"mission_id": missions["resume"].id},
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
                    "payload": {"mission_id": missions["documents"].id},
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
                    "payload": {"mission_id": missions["resume"].id},
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
                    "payload": {"mission_id": missions["documents"].id},
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
                    "payload": {"mission_id": missions["documents"].id},
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

    created_users = []
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
        created_users.append(user)

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

    return created_users
