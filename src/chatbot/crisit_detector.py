CRISIS_KEYWORDS = {"hopeless", "suicide", "self-harm", "drop out", "give up", "end it", "kill myself"}

def detect_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)