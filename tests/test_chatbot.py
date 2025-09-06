def test_crisis_detector():
    from src.chatbot.crisis_detector import detect_crisis
    assert detect_crisis("I feel hopeless") is True
    assert detect_crisis("I'm fine") is False