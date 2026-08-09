import os
import subprocess

APP_INDEX = {}

# -------------------------------
# Human-friendly aliases
# -------------------------------
ALIASES = {
    "notepad": "notepad",
    "calculator": "calculator",
    "calc": "calculator",
    "paint": "paint",
    "chrome": "chrome",
    "google": "chrome",
    "edge": "msedge",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "ppt": "powerpnt",
    "outlook": "outlook",
    "photos": "microsoft.photos",
    "photo": "microsoft.photos",
    "settings": "systemsettings",
    "clock": "windowsalarms",
    "calendar": "windowscommunicationsapps",
    "spotify": "spotify",
    "whatsapp": "whatsapp",
}

# -------------------------------
# UWP / Store apps
# -------------------------------
UWP_APPS = {
    "systemsettings": "windows.immersivecontrolpanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel",
    "microsoft.photos": "microsoft.windows.photos_8wekyb3d8bbwe!app",
    "windowsalarms": "microsoft.windowsalarms_8wekyb3d8bbwe!app",
    "spotify": "spotifyab.spotify_music_zpdnekdrzrea0!spotify",
    "whatsapp": "5319275a.WhatsAppDesktop_cv1g1gvanyjgm!App",
}

# -------------------------------
# Search paths
# -------------------------------
SEARCH_DIRS = [
    os.environ.get("ProgramFiles", ""),
    os.environ.get("ProgramFiles(x86)", ""),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
]

# -------------------------------
# Build app index
# -------------------------------
def build_app_index():
    APP_INDEX.clear()
    print("🔎 Indexing installed applications...")

    for base in SEARCH_DIRS:
        if not base or not os.path.exists(base):
            continue

        for root, _, files in os.walk(base):
            for file in files:
                if file.lower().endswith(".exe"):
                    name = os.path.splitext(file)[0].lower()
                    path = os.path.join(root, file)
                    if name not in APP_INDEX:
                        APP_INDEX[name] = path

    print(f"✅ Indexed {len(APP_INDEX)} applications")

# -------------------------------
# SAFE APP LAUNCHER
# -------------------------------
def open_app(app_name: str) -> bool:
    app_name = app_name.lower().strip()

    # Resolve alias
    app_key = ALIASES.get(app_name, app_name)

    # -------------------------------
    # UWP / Store apps
    # -------------------------------
    if app_key in UWP_APPS:
        try:
            subprocess.Popen(
                f'explorer.exe shell:AppsFolder\\{UWP_APPS[app_key]}',
                shell=True
            )
            return True
        except Exception as e:
            print("❌ UWP launch error:", e)
            return False

    # -------------------------------
    # Direct exe match
    # -------------------------------
    if app_key in APP_INDEX:
        try:
            subprocess.Popen(
                APP_INDEX[app_key],
                shell=True
            )
            return True
        except Exception as e:
            print("❌ App launch error:", e)
            return False

    # -------------------------------
    # Partial name match
    # -------------------------------
    for name, path in APP_INDEX.items():
        if app_key in name:
            try:
                subprocess.Popen(path, shell=True)
                return True
            except Exception as e:
                print("❌ App launch error:", e)
                return False

    print(f"⚠️ App '{app_name}' not found.")
    return False
