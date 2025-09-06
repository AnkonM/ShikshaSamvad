from flask import Flask, request, jsonify
from .nlu_model import SentimentAnalyzer
from .crisis_detector import detect_crisis

app = Flask(__name__)
sentiment = SentimentAnalyzer()

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/analyze")
def analyze():
    data = request.get_json(force=True)
    text = data.get("text", "")
    res = sentiment.analyze(text)
    res["crisis"] = detect_crisis(text)
    return jsonify(res)

@app.post("/chat")
def chat():
    data = request.get_json(force=True)
    text = data.get("text", "")
    if detect_crisis(text):
        return jsonify({"reply": "I’m here for you. I'm escalating this to a counselor immediately.", "escalate": True})
    # Placeholder rules; replace with Rasa integration
    if "stress" in text.lower():
        return jsonify({"reply": "Try 4-7-8 breathing. Would you like a short mindfulness exercise?", "escalate": False})
    return jsonify({"reply": "How are you feeling today?", "escalate": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)