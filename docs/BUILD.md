# Сборка APK

Buildozer работает только на Linux/macOS, на Windows — через WSL2 или GitHub Actions.

## Вариант A: GitHub Actions (проще всего на Windows)
1. Создайте репозиторий на GitHub и загрузите туда папку проекта (файл `.github/workflows/build-apk.yml` уже есть).
2. Вкладка **Actions → Build APK → Run workflow**.
3. Через 15–30 минут скачайте APK в разделе **Artifacts** (`studentapp-apk`).

## Вариант B: WSL2 (Ubuntu)
    sudo apt update
    sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config \
        zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev
    pip3 install --user buildozer cython==0.29.36
    cd /mnt/c/путь/к/student_app    # лучше скопировать проект в домашний каталог WSL
    buildozer android debug         # первая сборка долгая (скачивает SDK/NDK)

APK появится в `bin/`. Установка на телефон: `buildozer android deploy run` (с USB-отладкой)
или перенесите APK на телефон вручную.

## Известные нюансы
- Android 13+: при первом запуске приложение запросит разрешение на уведомления.
- Напоминания о дедлайнах приходят, пока приложение запущено (в фоне при закрытом приложении —
  потребуется AlarmManager, это отдельное расширение).
- Данные хранятся локально на устройстве (SQLite), чат работает между аккаунтами на одном устройстве.
- Смена шкалы оценок: `core/config.py → MAX_GRADE`.
