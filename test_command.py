from core.command_handler import handle_command

# Test Notepad
if handle_command("open notepad"):
    print("✅ Notepad opened")

# Test screenshot
if handle_command("take screenshot"):
    print("✅ Screenshot taken")

# Test search
if handle_command("search python programming"):
    print("✅ Search opened")
