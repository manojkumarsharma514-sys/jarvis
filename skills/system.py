import subprocess
import os
import pyautogui

# Full paths for common apps
apps = {
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": r"C:\Windows\SystemApps\Microsoft.WindowsCalculator_8wekyb3d8bbwe\CalculatorApp.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # Add more apps here
}

def handle(data):
    action = data.get("action")
    target = data.get("target").lower()
    print("⚙️ System action:", action, target)

    if action == "open app":
        path = apps.get(target)
        if path:
            subprocess.Popen(path)
        else:
            print(f"❌ Unknown app: {target}")

    elif action == "screenshot":
        pyautogui.screenshot("screenshot.png")
        print("📸 Screenshot saved")
