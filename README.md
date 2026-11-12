# Student App — организация учебного процесса и контроль успеваемости (Kivy + KivyMD)

Запуск на десктопе (Windows):

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

Модули (подключаются автоматически из `modules/*/module.py`): расписание, успеваемость,
дедлайны с напоминаниями, чат студент↔преподаватель, аналитика и отчёты.
Новый модуль: создайте `modules/<name>/module.py` с функцией `register(registry)`.

Сборка APK: см. `docs/BUILD.md`.
