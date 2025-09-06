from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self, model: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self.pipe = pipeline("sentiment-analysis", model=model)

    def analyze(self, text: str):
        result = self.pipe(text)[0]
        return {"label": result["label"], "score": float(result["score"])}