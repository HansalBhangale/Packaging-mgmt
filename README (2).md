# 📦 PackManager — Setup, Run & Share Guide

A KivyMD + MongoDB Atlas CRUD app for managing packed items and carton locations.

---

## Project Structure

```
packaging_app/
├── main.py          ← App logic + UI (KV string embedded)
├── database.py      ← MongoDB layer (threaded, singleton)
├── buildozer.spec   ← Android APK build config
└── README.md        ← This file
```

---

## STEP 1 — MongoDB Atlas Setup

1. Go to https://www.mongodb.com/cloud/atlas and create a **free cluster**.
2. Create a database user under **Database Access** (e.g. user: `packuser`, pass: `mypassword`).
3. Under **Network Access** → Add IP: `0.0.0.0/0` (allow anywhere — required for mobile).
4. Click **Connect → Connect your application** → copy the connection string.
5. Open `database.py` and replace `MONGO_URI`:

```python
MONGO_URI = (
    "mongodb+srv://packuser:mypassword"
    "@cluster0.abcde.mongodb.net/packaging_db"
    "?retryWrites=true&w=majority"
)
```

---

## STEP 2 — Run on Desktop (PC / Mac / Linux)

### 2a. Install dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install packages
pip install kivy==2.3.0 kivymd==1.1.1 pymongo dnspython certifi pillow
```

### 2b. Run the app

```bash
cd packaging_app
python main.py
```

The app window opens. You will see a snackbar: **"Connected to MongoDB Atlas ✓"**

---

## STEP 3 — Using the App

| Tab | Purpose |
|-----|---------|
| **Search** | Type any item name → live fuzzy results showing Carton + Location |
| **Inventory** | Scrollable full list — tap any item to Edit or Delete |
| **Add Item** | Enter item name, tap Carton field to pick from dropdown |
| **Cartons** | Map a Carton ID to a physical location; tap to edit/delete |

### Typical workflow:
1. Go to **Cartons** tab → add `BOX-01 → Garage Shelf B`
2. Go to **Add Item** → enter `Blue Hammer`, pick `BOX-01`
3. Go to **Search** → type `hammer` → see: *Carton: BOX-01 | Location: Garage Shelf B*

---

## STEP 4 — Build the Android APK

You need a **Linux machine** (or WSL2 on Windows, or a Docker container).

### 4a. Install Buildozer

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo6 cmake libffi-dev libssl-dev

pip install buildozer cython==0.29.33
```

### 4b. Build the APK

```bash
cd packaging_app
buildozer -v android debug
```

This takes **15–30 minutes** the first time (downloads Android SDK/NDK).

The APK will be at:
```
packaging_app/bin/packmanager-1.0.0-arm64-v8a-debug.apk
```

---

## STEP 5 — Install on Android Phone

### Method A — USB Cable
```bash
# Enable Developer Mode + USB Debugging on your phone
adb install bin/packmanager-1.0.0-arm64-v8a-debug.apk
```

### Method B — Transfer via any of these ways:

| Method | How |
|--------|-----|
| **Google Drive** | Upload the APK → open Drive on phone → tap to install |
| **WhatsApp / Telegram** | Send the APK file to yourself → tap to install |
| **Email** | Attach .apk → open on phone → tap to install |
| **USB File Transfer** | Copy APK to phone storage → use Files app to install |
| **Local HTTP server** | `python -m http.server 8080` → open `http://<your-ip>:8080` in phone browser → download & install |

> ⚠️ On Android, go to **Settings → Security → Install unknown apps** and allow your file manager or browser to install APKs.

---

## STEP 6 — Share the App with Others

### Option A: Share the Debug APK directly
- Upload the `.apk` to Google Drive / Dropbox / OneDrive
- Share the link
- Recipients enable "Unknown Sources" in their Android settings and install

### Option B: Publish on Google Play (Production)
```bash
# Build a release APK
buildozer android release

# Sign the APK with your keystore
keytool -genkey -v -keystore my-release.jks -alias packmanager \
        -keyalg RSA -keysize 2048 -validity 10000

jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
          -keystore my-release.jks \
          bin/packmanager-1.0.0-arm64-v8a-release-unsigned.apk packmanager

zipalign -v 4 bin/*release-unsigned.apk bin/packmanager-release.apk
```
Then upload `packmanager-release.apk` to the Google Play Console.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot reach MongoDB Atlas" | Check internet; ensure `0.0.0.0/0` is in Atlas IP whitelist |
| SSL certificate error on Android | Already handled — `certifi.where()` is used in `database.py` |
| App crashes on launch | Run `adb logcat` to see Python traceback |
| Buildozer fails | Make sure you're on Linux; try `buildozer android clean` then rebuild |
| APK won't install | Enable "Install unknown apps" in Android settings |

---

## Requirements Summary

```
kivy==2.3.0
kivymd==1.1.1
pymongo
dnspython
certifi
pillow
```

MongoDB Atlas: Free M0 cluster is sufficient for hundreds of items.
