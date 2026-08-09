import webbrowser

def handle(data):
    query = data.get("target")
    webbrowser.open(f"https://www.google.com/search?q={query}")
    print("🌐 Searching Google:", query)
