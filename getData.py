"""
Тут филтры работают как сито
Есть обязательные ключевые слова, есть необязательные
Задача на ранних этап отсеят мусор, и достать только то, что
нужно
"""

import json
from models import Vacancy
from typing import Literal


def filter_vacancy(name: str) -> bool:
    "Фильтр названий вакансий"

    name_lower = name.lower()

    # Tier-1 — сразу нет
    tier1 = [
        "1c",
        "qt",
        "c#",
        "c++",
        "java",
        "php",
        "ruby",
        "golang",
        "swift",
        "kotlin",
        "frontend",
        "react",
        "angular",
        "vue",
        "ai",
        "преподаватель",
        "sdet",
        "sdet",
        "seo",
        "моделирование",
        "fullstack",
        "тестирование",
        "ml",
        "llm",
        "quant",
        "trading",
        "автотестирован",
        "автоматизации тестирования",
        "по автотестированию",
    ]
    if any(kw in name_lower for kw in tier1):
        return False

    current_vacansy = ["python", "питон"]
    if not any(kw in name_lower for kw in current_vacansy):
        return False

    # Must-have hits
    must_have = [
        "python",
        "backend",
        "fastapi",
        "django",
        "aiogram",
        "asyncio",
        "litestar",
        "developer",
        "разработчик",
    ]
    hits = sum(1 for kw in must_have if kw in name_lower)

    # Tier-2 — нет если меньше 2 must-have
    tier2 = [
        "sql",
        "vba",
        "data engineer",
        "стажёр",
        "стажер",
        "senior",
        "аналитик",
        "тестировщик",
        "qa",
        "devops",
        "администратор",
    ]
    if any(kw in name_lower for kw in tier2) and hits < 2:
        return False

    return True


def get_needed_vacancies(
    wrk_form: list[Literal["ON_SITE", "REMOTE", "HYBRID"]] = [
        "ON_SITE",
        "REMOTE",
        "HYBRID",
    ],
    same_company: bool = True,
    limit: int | None = None,
) -> list[Vacancy]:
    """Филтр для параметров вакансий и определённого списка

    Args:
        wrk_form (str) : В такой форме API HH отдаёт место работы, по умолчанию все варианты
        same_company (bool) : True : Разрешение или запрет на повторяющееся компании
        limit (int) : None : Ограничение на количество вакансий
    """
    result = []
    comp_holder = set()

    with open("vacancies.json", "r") as f:
        raw = json.load(f)

    vacancies = [Vacancy.from_raw(v) for v in raw]

    for v in vacancies:
        if not filter_vacancy(v.name):
            continue
        if not any(kw in wrk_form for kw in v.work_formats):
            continue
        if not same_company:
            if v.company in comp_holder:
                continue
            comp_holder.add(v.company)
        result.append(v)
        if limit and len(result) >= limit:
            break

    return result


if __name__ == "__main__":
    res = get_needed_vacancies(limit=10)
