import os

def handle(data):
    path = data.get("target")
    try:
        os.startfile(path)
        print("📁 Folder opened:", path)
    except Exception as e:
        print("❌ Could not open folder:", path, e)
