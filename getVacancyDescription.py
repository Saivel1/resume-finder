"""
Запросы идут батчами, то есть несколько за раз

"""

import asyncio
import json
import aiohttp
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from getData import get_needed_vacancies
from parser import HEADERS


# https://yandex.cloud/ru/docs/iam/operations/iam-token/create?&utm_referrer=https%3A//www.google.com/
YANDEX_FOLDER_ID = ""
YANDEX_OAUTH_TOKEN = ""


PROFILE = """
Python Backend разработчик, 2 года 5 месяцев опыта.

Текущий стек: FastAPI, asyncio, SQLAlchemy, Alembic, PostgreSQL, SQL, Redis, Celery, Aiogram, Docker Compose, pytest, Git.
Предыдущий опыт: Django, Django REST Framework, JWT, aiohttp.

Что делал:
- 50+ асинхронных REST API эндпоинтов на FastAPI
- Оптимизация PostgreSQL запросов (EXPLAIN ANALYZE, индексы, ORM)
- Redis кэширование (cache-aside), идемпотентная обработка платежей
- Интеграция с эквайрингом Т-Банка через webhook
- Микросервис уведомлений: Aiogram + Taskiq
- Docker Compose, unit/integration тесты pytest
- Django REST Framework: сериализаторы, ViewSet, JWT auth, RBAC
- Интеграция с внешним API СДЭК

Ищу: Python backend разработку, удалёнка или гибрид.
Зарплата: от 100к.
НЕ интересует: ML, QA/тестирование, DevOps, преподавание, аналитика.
"""

SYSTEM = """Ты помогаешь оценить вакансию для Python backend разработчика.
Оцени соответствие от 0 до 10 по таким критериям:

9-10: Python backend, знакомый стек как у меня в профиле, удалёнка, адекватная зарплата
7-8: Python backend но незнакомый стек или офис или зарплата ниже ожидаемой
5-6: Python есть но это не backend (ML, автоматизация, тестирование, аналитика)
3-4: Python упомянут вскользь, основной стек другой
1-2: Не подходит совсем (преподаватель, QA, DevOps)

ВАЖНО: если навык упомянут в профиле кандидата — не считай его минусом.
Отвечай ТОЛЬКО валидным JSON без markdown: {"score": 7.2, "reason": "..."}
Reason на русском, 2-3 предложения."""


async def fetch_description(session: AsyncSession, vacancy_id: int) -> str:
    url = f"https://hh.ru/vacancy/{vacancy_id}"
    headers = {
        **HEADERS,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://hh.ru/search/vacancy",
    }
    headers.pop("X-Requested-With", None)
    headers.pop("X-hhtmFrom", None)

    resp = await session.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"vacancy {vacancy_id} failed: {resp.status_code}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    block = soup.find(attrs={"data-qa": "vacancy-description"})
    return block.get_text(separator="\n", strip=True) if block else ""


async def get_iam_token(session: aiohttp.ClientSession):
    async with session.post(
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        json={"yandexPassportOauthToken": YANDEX_OAUTH_TOKEN},
    ) as res:
        js = await res.json()
        return js["iamToken"]


async def score_vacancy(description: str, name: str) -> dict:
    prompt = f"Мой профиль: {PROFILE}\n\nВакансия: {name}\nОписание: {description}"

    async with aiohttp.ClientSession() as session:
        IAM_TOKEN = await get_iam_token(session=session)
        async with session.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Bearer {IAM_TOKEN}",
                "x-folder-id": YANDEX_FOLDER_ID,
            },
            json={
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.0,
                    "maxTokens": 500,
                },
                "messages": [
                    {"role": "system", "text": SYSTEM},
                    {"role": "user", "text": prompt},
                ],
            },
        ) as resp:
            data = await resp.json()
            content = data["result"]["alternatives"][0]["message"]["text"]
            content = content.strip()
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)


async def process_vacancy(session: AsyncSession, v) -> dict | None:
    desc = await fetch_description(session, v.id)
    if not desc:
        return None

    scored = await score_vacancy(desc, v.name)
    if scored["score"] < 7.0:
        print(f"SKIP {scored['score']} {v.name}")
        return None

    print(f"OK   {scored['score']} {v.name}")
    return {
        "id": v.id,
        "name": v.name,
        "company": v.company,
        "url": v.url,
        "compensation": v.compensation.model_dump() if v.compensation else None,
        **scored,
    }


async def main():
    vacancies = get_needed_vacancies()
    print(f"Всего после фильтрации: {len(vacancies)}")

    results = []
    # Должна быть константой.
    batch_size = 5

    async with AsyncSession(impersonate="firefox") as session:
        for i in range(0, len(vacancies), batch_size):
            batch = vacancies[i : i + batch_size]
            print(
                f"\nБатч {i // batch_size + 1}/{(len(vacancies) + batch_size - 1) // batch_size}"
            )
            batch_results = await asyncio.gather(
                *[process_vacancy(session, v) for v in batch]
            )
            results.extend([r for r in batch_results if r is not None])
            await asyncio.sleep(1.0)

    results.sort(key=lambda x: x["score"], reverse=True)

    with open("scored.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nИтого подходящих: {len(results)}")
    for r in results:
        print(f"{r['score']} {r['name']} — {r['url']}")


if __name__ == "__main__":
    asyncio.run(main())
