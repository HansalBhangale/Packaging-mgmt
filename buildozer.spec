[app]

# ─── Identity ────────────────────────────────────────────────────────────────
title = PackManager
package.name = packmanager
package.domain = com.yourname
version = 1.0.0

# ─── Source ──────────────────────────────────────────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# ─── Python / Kivy Version ───────────────────────────────────────────────────
requirements = python3,\
    kivy==2.3.0,\
    kivymd==1.1.1,\
    pymongo,\
    dnspython,\
    certifi,\
    openssl,\
    pillow

# ─── Android Settings ────────────────────────────────────────────────────────
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25c
android.arch = arm64-v8a

# ─── Orientation + Screen ────────────────────────────────────────────────────
orientation = portrait
fullscreen = 0

# ─── Icons (replace with your own) ──────────────────────────────────────────
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# ─── Build mode ──────────────────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1
