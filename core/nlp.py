import re
from difflib import get_close_matches

# Words to ignore completely
GARBAGE_WORDS = [
    "please", "can", "could", "you", "for", "me",
    "sir", "hey", "jarvis", "kindly"
]

# Known command keywords
INTENTS = {
    "close": ["close", "exit", "quit", "shutdown"],
    "open": ["open", "start", "run", "launch"],
    "screenshot": ["screenshot", "screen", "capture"],
    "search": ["search", "google", "find"],
}

# 🔹 NEW: Known words for fuzzy correction
KNOWN_WORDS = [
    "open", "close", "window", "chrome", "edge",
    "excel", "word", "powerpoint", "notepad",
    "calculator", "paint", "settings",
    "spotify", "whatsapp", "google",
    "knowledge", "search", "screenshot"
]

# -------------------------
# Existing cleaning logic
# -------------------------
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)

    words = text.split()
    words = [w for w in words if w not in GARBAGE_WORDS]

    return " ".join(words)


# -------------------------
# Existing intent detection
# -------------------------
def detect_intent(text: str) -> str | None:
    for intent, keywords in INTENTS.items():
        for word in text.split():
            if get_close_matches(word, keywords, n=1, cutoff=0.75):
                return intent
    return None


# -------------------------
# 🔹 NEW: Fuzzy word correction
# -------------------------
def fuzzy_correct_word(word: str) -> str:
    match = get_close_matches(word, KNOWN_WORDS, n=1, cutoff=0.75)
    return match[0] if match else word


def fuzzy_correct_sentence(text: str) -> str:
    return " ".join(fuzzy_correct_word(w) for w in text.split())


# -------------------------
# Final normalization (UPDATED)
# -------------------------
def normalize_command(text: str) -> str:
    # Step 1: clean garbage words
    text = clean_text(text)

    # Step 2: fuzzy auto-correction
    text = fuzzy_correct_sentence(text)

    # Step 3: Normalize open intent
    for word in ["start", "run", "launch"]:
        if text.startswith(word + " "):
            text = text.replace(word, "open", 1)

    # Step 4: Fix bad recognitions like "yogesh window"
    if "window" in text and any(w in text for w in ["yogesh", "yojish", "yogesh"]):
        return "close window"

    # Step 5: Normalize close window
    if "close" in text and "window" in text:
        return "close window"

    return text
