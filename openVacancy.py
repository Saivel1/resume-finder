"""
Здесь просто скрипт для открытия дефолтным браузером ссылок
работает, просто как дабл-клик
"""

import webbrowser
import json


def a_func():
    "Функция для запуска скрипта"
    with open("scored.json", "r") as f:
        scored = json.load(f)

    scored.sort(key=lambda x: x["score"], reverse=True)

    for v in scored:
        print(f"{v['score']} {v['name']} — {v['url']}")
        webbrowser.open(v["url"])


if __name__ == "__main__":
    "Не даёт исполняться части ниже при импорте, только при выполнении этого скрипта"
    a_func()

