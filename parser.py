"""
Тут функции написанны асинхронно, но можно переделать всё пол
request будет проще для восприятия, и понимания
"""

import asyncio
import json
from curl_cffi.requests import AsyncSession

# Эту часть нужно будет заполнить своими данными
COOKIE_STRING = '__ddg1_=; regions=""; region_clarified=NOT_SET; hhtoken=; hhuid=; ...'  # полная строка из нового запроса

# Заголовки также достать из бразуера
HEADERS = {
    "User-Agent": "",
    "Accept": "application/json",
    "Accept-Language": "ru,en-US;q=0.9,en;q=0.8",
    "X-hhtmSource": "",
    "X-hhtmFrom": "",
    "X-hhtmFromLabel": "",
    "X-Requested-With": "",
    "X-Static-Version": "",
    "X-Xsrftoken": "",
    "Referer": "https://hh.ru/search/vacancy?page=0",
    "Cookie": COOKIE_STRING,
}


# Строка запроса с фильтрами разбитая на отрезки
BASE_URL = (
    "https://hh.ru/search/vacancy"
    "?resume=ТВОЙ ИДЕНТИФИКАТОР РЕЗЮМЕ"
    "&experience=between1And3"
    "&search_field=name"
    "&search_field=company_name"
    "&search_field=description"
    "&enable_snippets=false"
    "&forceFiltersSaving=true"
    "&search_session_id= ТВОЙ ID"
)


async def fetch_page(session: AsyncSession, page: int, retries: int = 3) -> list:
    "Получение данных с ретрай логикой"
    for attempt in range(retries):
        resp = await session.get(BASE_URL + f"&page={page}", headers=HEADERS)
        if resp.status_code == 200:
            return resp.json()["vacancySearchResult"]["vacancies"]
        print(f"page {page} attempt {attempt + 1} failed: {resp.status_code}, ждём...")
        await asyncio.sleep(2**attempt)  # 1s, 2s, 4s
    print(f"page {page} окончательно не загрузилась")
    return []


async def fetch_all_vacancies() -> list:
    "Получаем данные для парсинга, а также создаём задачи"

    all_vacancies = []
    # Тут нужно выбрать тот бразуер под который ты маскируешся
    async with AsyncSession(impersonate="firefox") as session:
        # первая страница с retry
        for attempt in range(3):
            resp = await session.get(BASE_URL + "&page=0", headers=HEADERS)
            if resp.status_code == 200:
                break
            print(f"page 0 attempt {attempt + 1} failed, ждём...")
            await asyncio.sleep(2**attempt)
        else:
            print("page 0 окончательно не загрузилась")
            return []

        data = resp.json()
        all_vacancies.extend(data["vacancySearchResult"]["vacancies"])

        total = data["vacancySearchResult"]["totalResults"]
        total_pages = (total + 49) // 50
        print(f"Всего вакансий: {total}, страниц: {total_pages}")

        for page in range(1, total_pages):
            # Делаем запросы ко всем страницам, поиска. Аналог цифры снизу поиска от 1 до последней
            # Запросов делаем мало, поэтому делаем их последовательно. Легко заменяется на синхронную функцию
            vacancies = await fetch_page(session, page)
            all_vacancies.extend(vacancies)
            print(f"Страница {page}/{total_pages - 1}: +{len(vacancies)} вакансий")
            await asyncio.sleep(1.0)

    print(f"Итого собрано: {len(all_vacancies)}")
    return all_vacancies


if __name__ == "__main__":
    vacancies = asyncio.run(fetch_all_vacancies())
    with open("vacancies.json", "w") as f:
        json.dump(vacancies, f, ensure_ascii=False, indent=2)
