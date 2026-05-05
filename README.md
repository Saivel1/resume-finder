Resources:

| Название | Ссылка | Что получишь |
|-----------|:-----------:|-----------|
| Статья про деко | https://habr.com/ru/articles/141411/| Что такое декораторы в python |
| Типизация| https://to.digital/typed-python/|Что такое типизация, и как её применять. БАЗА|
| Командая строка под WSL|https://ru.hexlet.io/programs/cli-basics | Оснавная работа на серверах будет под Linux |
| Настройка VS Code | https://stepik.org/lesson/759383/step/1?unit=761399| В том числе как поставить правильный интерпретатор, и командую строку|
| I-am token Yandex | https://yandex.cloud/ru/docs/iam/operations/iam-token/create?&utm_referrer=https%3A//www.google.com/ | Для запросов к API яндекс GPT|
| uv | https://docs.astral.sh/uv/getting-started/installation/| самый быстрый менеджер пакетов для python, вместо/вместе с pip|



После установки uv
```
uv sync
```

Виртуальное окружение
```
source .venv/bin/activate 
```


Pipeline
```
parser -> getData -> getVacancyDescription -> openVacancys
```

Все этапы создают артефакты, в виде JSON файлов, кроме последнего. 
