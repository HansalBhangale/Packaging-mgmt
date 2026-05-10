# PackManager — Build APK on Google Colab
# Run each cell one by one. Total time: ~25 minutes.
# Open this at: https://colab.research.google.com

# ── CELL 1: Install system dependencies ──────────────────────────────────────
%%bash
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3-pip git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    cmake libffi-dev libssl-dev
echo "✓ System deps installed"

# ── CELL 2: Install Python build tools ───────────────────────────────────────
%%bash
pip install -q buildozer cython==0.29.33
echo "✓ Buildozer installed"

# ── CELL 3: Upload your project files ────────────────────────────────────────
# Run this cell — it will show an "Upload" button
from google.colab import files
uploaded = files.upload()
# Upload: main.py and database.py (and icon.png if you have one)

# ── CELL 4: Create the buildozer.spec ────────────────────────────────────────
spec = """
[app]
title = PackManager
package.name = packmanager
package.domain = com.yourname
version = 1.0.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
requirements = python3,kivy==2.3.0,kivymd==1.1.1,pymongo,dnspython,certifi,openssl,pillow
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25c
android.arch = arm64-v8a
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
"""

with open("buildozer.spec", "w") as f:
    f.write(spec.strip())
print("✓ buildozer.spec created")

# ── CELL 5: Build the APK (takes ~20 min first time) ─────────────────────────
%%bash
buildozer -v android debug 2>&1 | tail -40

# ── CELL 6: Download the APK to your computer ────────────────────────────────
import glob
from google.colab import files

apk_files = glob.glob("bin/*.apk")
if apk_files:
    print(f"✓ Found APK: {apk_files[0]}")
    files.download(apk_files[0])
else:
    print("✗ No APK found — check build errors above")
