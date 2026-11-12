[app]
title = Учебный процесс
package.name = studentapp
package.domain = org.university
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = docs,venv,.github,__pycache__,bin
version = 0.1.0
# sqlite3 нужен для БД, plyer — для уведомлений, pillow — зависимость KivyMD.
# Если сборка ругается на kivymd==1.2.0, замените на:
#   https://github.com/kivymd/KivyMD/archive/1.2.0.zip
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,plyer,sqlite3
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/splash.png
orientation = portrait
fullscreen = 0

android.permissions = POST_NOTIFICATIONS
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
