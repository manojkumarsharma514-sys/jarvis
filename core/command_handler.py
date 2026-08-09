import subprocess
import webbrowser
import pyautogui
import os
import time
from difflib import get_close_matches
import pygetwindow as gw  # ✅ Added for window switching

from core.app_launcher import open_app
import core.state as state


# -------------------------------
# OPTIONAL AI GRAMMAR (SAFE)
# -------------------------------
try:
    import language_tool_python
    _tool = language_tool_python.LanguageTool('en-US')
except:
    _tool = None


def grammar_correct(text: str) -> str:
    if not _tool:
        return text
    try:
        return _tool.correct(text)
    except:
        return text


# -------------------------------
# WORD AUTO-CORRECTION
# -------------------------------
COMMON_WORDS = [
    "chrome", "notepad", "calculator", "excel", "word", "powerpoint",
    "open", "close", "search", "type", "write", "window", "minimize",
    "google", "screenshot", "downloads", "desktop", "documents",
    "pictures", "videos", "pdf", "file", "folder",
    "switch", "next", "previous", "tab", "click"
]


def autocorrect_word(word: str) -> str:
    match = get_close_matches(word, COMMON_WORDS, n=1, cutoff=0.75)
    return match[0] if match else word


def autocorrect_sentence(text: str) -> str:
    return " ".join(autocorrect_word(w) for w in text.split())


# -------------------------------
# CONTEXT HELPERS ✅ ADDED
# -------------------------------
def is_context_close(query: str) -> bool:
    return query.strip() in ["close it", "close this", "close that"]


# -------------------------------
# SWITCH TO WINDOW BY APP NAME
# -------------------------------
def switch_to_window(app_name: str) -> bool:
    try:
        windows = gw.getWindowsWithTitle(app_name)
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            print(f"🔀 Switched to window: {app_name}")
            return True
    except Exception as e:
        print("❌ Window switch error:", e)
    return False


# -------------------------------
# DYNAMIC TYPING DELAY
# -------------------------------
def get_typing_interval() -> float:
    try:
        active_window = gw.getActiveWindow()
        if not active_window:
            return 0.05
        title = active_window.title.lower()
        if "excel" in title or "word" in title:
            return 0.1
    except:
        pass
    return 0.05


# -------------------------------
# MAIN COMMAND HANDLER
# -------------------------------
def handle_command(query: str) -> bool:

    query = query.lower().strip()
    query = autocorrect_sentence(query)

    # -------------------------------
    # CONTEXT COMMANDS (FIXED ✅)
    # -------------------------------
    if is_context_close(query) and state.last_app:
        pyautogui.hotkey("alt", "f4")
        print(f"❌ Closed last app: {state.last_app}")
        return True

    if "open it again" in query and state.last_app:
        open_app(state.last_app)
        print(f"🔁 Reopened {state.last_app}")
        return True

    # -------------------------------
    # SWITCH WINDOW BY NAME
    # -------------------------------
    if query.startswith(("switch to ", "go to ", "change window to ")):
        app_name = (
            query.replace("switch to", "")
                 .replace("go to", "")
                 .replace("change window to", "")
                 .strip()
        )
        if app_name:
            switch_to_window(app_name)
            return True

    # -------------------------------
    # SWITCH / CHANGE WINDOW (ALT+TAB)
    # -------------------------------
    if "switch window" in query or "next window" in query:
        pyautogui.hotkey("alt", "tab")
        return True

    if "previous window" in query:
        pyautogui.hotkey("alt", "shift", "tab")
        return True

    # -------------------------------
    # BROWSER TAB CONTROL
    # -------------------------------
    if "next tab" in query:
        pyautogui.hotkey("ctrl", "tab")
        return True

    if "previous tab" in query:
        pyautogui.hotkey("ctrl", "shift", "tab")
        return True

    # -------------------------------
    # CLOSE SPECIFIC APPLICATION (SAFE)
    # -------------------------------
    if (
        query.startswith("close ")
        and "window" not in query
        and not is_context_close(query)
    ):
        app_name = query.replace("close", "").strip()
        if app_name:
            subprocess.call(
                f'taskkill /f /im {app_name}.exe',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            state.last_app = app_name
            print(f"❌ Closed app: {app_name}")
            return True

    # -------------------------------
    # OPEN FOLDERS
    # -------------------------------
    FOLDER_ALIASES = {
        "desktop": os.path.join(os.environ["USERPROFILE"], "Desktop"),
        "downloads": os.path.join(os.environ["USERPROFILE"], "Downloads"),
        "documents": os.path.join(os.environ["USERPROFILE"], "Documents"),
        "pictures": os.path.join(os.environ["USERPROFILE"], "Pictures"),
        "videos": os.path.join(os.environ["USERPROFILE"], "Videos"),
    }

    if query.startswith("open "):
        folder_name = query.replace("open", "").strip()
        if folder_name in FOLDER_ALIASES:
            os.startfile(FOLDER_ALIASES[folder_name])
            return True

    # -------------------------------
    # OPEN APPLICATIONS
    # -------------------------------
    if query.startswith("open "):
        app_name = query.replace("open", "").strip()
        if app_name:
            if open_app(app_name):
                state.last_app = app_name
            return True

    # -------------------------------
    # GOOGLE SEARCH
    # -------------------------------
    if query.startswith("search "):
        webbrowser.open(
            f"https://www.google.com/search?q={query.replace('search','').strip()}"
        )
        return True

    # -------------------------------
    # SCREENSHOT
    # -------------------------------
    if "screenshot" in query:
        pyautogui.screenshot("screenshot.png")
        return True

    # -------------------------------
    # MOUSE CLICK
    # -------------------------------
    if "click" in query:
        pyautogui.click()
        return True

    # -------------------------------
    # TYPE WITH AI GRAMMAR
    # -------------------------------
    if query.startswith("type") or query.startswith("write"):
        text = query.replace("type", "").replace("write", "").strip()
        corrected = grammar_correct(text)
        time.sleep(0.2)
        pyautogui.write(corrected, interval=get_typing_interval())
        return True

    # -------------------------------
    # SCROLL
    # -------------------------------
    if "scroll down" in query:
        pyautogui.scroll(-600)
        return True

    if "scroll up" in query:
        pyautogui.scroll(600)
        return True

    # -------------------------------
    # WINDOW CONTROLS
    # -------------------------------
    if "close window" in query:
        pyautogui.hotkey("alt", "f4")
        return True

    if "minimize window" in query:
        pyautogui.hotkey("win", "down")
        return True

    # -------------------------------
    # SYSTEM
    # -------------------------------
    if "shutdown" in query:
        os.system("shutdown /s /t 5")
        return True

    if "restart" in query:
        os.system("shutdown /r /t 5")
        return True

    return False
