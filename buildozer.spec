[app]
title = HTOOL NOVA
package.name = htoolnova
package.domain = org.htool
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,ini,ttf,otf
source.exclude_dirs = .git,bin,.buildozer,__pycache__,.venv
version = 3.0
requirements = python3,kivy,pytz,requests,websocket-client,rich,cryptography
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
