mkdir -p /workspace/Shikshasamvaad/{config,data/raw,data/processed,notebooks,src/{risk_engine,chatbot/rasa,dashboard,database,utils},scripts,tests,deployments,models/risk_engine}
touch /workspace/Shikshasamvaad/src/{__init__.py,risk_engine/__init__.py,chatbot/__init__.py,dashboard/__init__.py,database/__init__.py,utils/__init__.py}

# README
cat > /workspace/Shikshasamvaad/README.md << 'EOF'
Shikshasamvaad: AI/ML-based Student Dropout Prediction and Counseling

Overview
Shikshasamvaad is an integrated platform for early detection of student dropout risk and continuous well-being support. It combines a Bayesian Neural Network risk assessment engine, an NLP counseling chatbot, and a faculty-facing wellness dashboard. The system supports SQLite for lightweight deployments and Firebase for cloud-based real-time sync.

Key Components
- AI Risk Assessment Engine: Bayesian Neural Network predicting dropout probability with uncertainty intervals, trained on attendance, grades, engagement, and activity features.
- NLP Counselling Chatbot: Built with Rasa and Hugging Face models, exposed via a Flask API. Provides CBT-inspired tips, mindfulness, and crisis escalation.
- Wellness Dashboard: Streamlit app visualizing risk trends, anonymized IDs, alerts, and monthly reports.
- Database Layer: SQLite and Firebase connectors for persistence and synchronization.

Getting Started
1) Environment:
- Conda: conda env create -f environment.yml && conda activate shikshasamvaad
- Pip: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

2) Generate sample data:
- python scripts/generate_lms_data.py

3) Ingest data:
- python scripts/ingest_lms_data.py --backend sqlite

4) Run services:
- bash scripts/run_chatbot.sh
- bash scripts/run_dashboard.sh

Notes
- Replace credentials in config/firebase_config.json before enabling Firebase.
- Rasa config in config/rasa_config.yml; intents in src/chatbot/rasa/.
- Modules are skeletons; fill implementations under src/.
EOF

# .gitignore
cat > /workspace/Shikshasamvaad/.gitignore << 'EOF'
__pycache__/
*.py[cod]
*.pyo
*.pyd
.venv/
venv/
env/
*.egg-info/
dist/
build/

data/raw/*.csv
data/processed/
notebooks/.ipynb_checkpoints/
reports/

config/firebase_config.json
.env

.DS_Store
Thumbs.db
.idea/
.vscode/

.rasa/
.cache/
.streamlit/
EOF

# requirements.txt
cat > /workspace/Shikshasamvaad/requirements.txt << 'EOF'
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
torch>=2.2.0
torchvision>=0.17.0
torchaudio>=2.2.0

transformers>=4.44.0
sentencepiece>=0.1.99
accelerate>=0.33.0
rasa>=3.6.0
nltk>=3.9
flask>=3.0.0

streamlit>=1.36.0
dash>=2.17.0
plotly>=5.22.0
matplotlib>=3.8.0

SQLAlchemy>=2.0.29
firebase-admin>=6.5.0
sqlite-utils>=3.36

python-dotenv>=1.0.1
pyyaml>=6.0.1
loguru>=0.7.2
reportlab>=4.2.0
fpdf2>=2.7.9

pytest>=8.2.0
pytest-cov>=5.0.0
EOF

# environment.yml
cat > /workspace/Shikshasamvaad/environment.yml << 'EOF'
name: shikshasamvaad
channels:
  - conda-forge
dependencies:
  - python>=3.9
  - pip
  - pip:
      - -r requirements.txt
EOF

# Configs
cat > /workspace/Shikshasamvaad/config/settings.yaml << 'EOF'
app:
  name: Shikshasamvaad
  environment: development
  log_level: INFO

data:
  raw_path: data/raw/lms_data.csv
  processed_path: data/processed/processed_lms.parquet

risk_engine:
  model_dir: models/risk_engine
  features:
    - attendance
    - avg_grade
    - submissions
    - last_activity_days

chatbot:
  language: en
  enable_crisis_detection: true

database:
  backend: sqlite
  sqlite:
    uri: sqlite:///data/processed/shikshasamvaad.db
  firebase:
    credentials_path: config/firebase_config.json

dashboard:
  host: 0.0.0.0
  port: 8501
EOF

cat > /workspace/Shikshasamvaad/config/firebase_config.json << 'EOF'
{
  "type": "service_account",
  "project_id": "REPLACE_ME",
  "private_key_id": "REPLACE_ME",
  "private_key": "REPLACE_ME",
  "client_email": "REPLACE_ME",
  "client_id": "REPLACE_ME",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "REPLACE_ME"
}
EOF

cat > /workspace/Shikshasamvaad/config/rasa_config.yml << 'EOF'
language: en
pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: LanguageModelFeaturizer
    model_name: distilbert
policies:
  - name: MemoizationPolicy
  - name: RulePolicy
  - name: TEDPolicy
EOF

# Notebooks (minimal JSON)
cat > /workspace/Shikshasamvaad/notebooks/risk_prediction.ipynb << 'EOF'
{"cells":[{"cell_type":"markdown","metadata":{},"source":["# Risk Prediction Notebook\n","Skeleton for BNN experiments.\n"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
EOF
cat > /workspace/Shikshasamvaad/notebooks/bnn_experiments.ipynb << 'EOF'
{"cells":[{"cell_type":"markdown","metadata":{},"source":["# BNN Experiments\n","Hyperparameters and uncertainty analysis.\n"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
EOF
cat > /workspace/Shikshasamvaad/notebooks/sentiment_analysis.ipynb << 'EOF'
{"cells":[{"cell_type":"markdown","metadata":{},"source":["# Sentiment Analysis Notebook\n","Model sanity checks for NLU.\n"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
EOF

# Risk Engine stubs
cat > /workspace/Shikshasamvaad/src/risk_engine/data_loader.py << 'EOF'
from pathlib import Path
import pandas as pd

def load_raw_lms(csv_path: str) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    return pd.read_csv(path)

def save_processed(df: pd.DataFrame, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
EOF

cat > /workspace/Shikshasamvaad/src/risk_engine/preprocess.py << 'EOF'
import pandas as pd
from datetime import datetime

def add_last_activity_days(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["last_activity"] = pd.to_datetime(df["last_activity"])
    df["last_activity_days"] = (pd.Timestamp(datetime.today().date()) - df["last_activity"]).dt.days
    return df

def select_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["attendance", "avg_grade", "submissions", "last_activity_days"]
    return df[cols].copy()
EOF

cat > /workspace/Shikshasamvaad/src/risk_engine/bnn_model.py << 'EOF'
from typing import Tuple
import torch
import torch.nn as nn

class SimpleBNN(nn.Module):
    """
    Placeholder Bayesian-like model. Replace with real Bayesian layers (e.g., pyro/pytorch distributions)
    or approximate inference strategy. For now, acts as a stub.
    """
    def __init__(self, input_dim: int, hidden_dim: int = 32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

def predict_with_uncertainty(model: nn.Module, x: torch.Tensor, num_samples: int = 30) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    MC-dropout style uncertainty as a stand-in. Replace with true BNN predictive distribution later.
    Returns mean, lower_ci, upper_ci.
    """
    model.train()  # enable dropout
    preds = []
    with torch.no_grad():
        for _ in range(num_samples):
            preds.append(model(x).squeeze(-1))
    samples = torch.stack(preds, dim=0)
    mean = samples.mean(dim=0)
    lower = samples.quantile(0.05, dim=0)
    upper = samples.quantile(0.95, dim=0)
    return mean, lower, upper
EOF

cat > /workspace/Shikshasamvaad/src/risk_engine/train.py << 'EOF'
from pathlib import Path
import pandas as pd
import torch
from torch.utils.data import TensorDataset, DataLoader
from .bnn_model import SimpleBNN
from .preprocess import add_last_activity_days, select_features

def train_dummy(input_path: str, model_dir: str) -> None:
    df = pd.read_csv(input_path)
    df = add_last_activity_days(df)
    X = select_features(df).values
    y = (df["avg_grade"] < 60).astype(int).values  # dummy target
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

    model = SimpleBNN(input_dim=X_t.shape[1])
    ds = TensorDataset(X_t, y_t)
    dl = DataLoader(ds, batch_size=16, shuffle=True)

    loss_fn = torch.nn.BCELoss()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    for _ in range(3):
        for xb, yb in dl:
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()

    out_dir = Path(model_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "model.pt")

if __name__ == "__main__":
    train_dummy("data/raw/lms_data.csv", "models/risk_engine")
EOF

cat > /workspace/Shikshasamvaad/src/risk_engine/predict.py << 'EOF'
from pathlib import Path
import pandas as pd
import torch
from .bnn_model import SimpleBNN, predict_with_uncertainty
from .preprocess import add_last_activity_days, select_features

def run_inference(input_path: str, model_dir: str, output_csv: str) -> None:
    df = pd.read_csv(input_path)
    df = add_last_activity_days(df)
    X = select_features(df).values
    X_t = torch.tensor(X, dtype=torch.float32)

    model = SimpleBNN(input_dim=X_t.shape[1])
    model.load_state_dict(torch.load(Path(model_dir) / "model.pt", map_location="cpu"))

    mean, lower, upper = predict_with_uncertainty(model, X_t, num_samples=20)
    df_out = df.copy()
    df_out["dropout_risk"] = mean.numpy()
    df_out["risk_ci_lower"] = lower.numpy()
    df_out["risk_ci_upper"] = upper.numpy()

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_csv, index=False)

if __name__ == "__main__":
    run_inference("data/raw/lms_data.csv", "models/risk_engine", "data/processed/risk_predictions.csv")
EOF

# Chatbot stubs
cat > /workspace/Shikshasamvaad/src/chatbot/nlu_model.py << 'EOF'
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self, model: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self.pipe = pipeline("sentiment-analysis", model=model)

    def analyze(self, text: str):
        result = self.pipe(text)[0]
        return {"label": result["label"], "score": float(result["score"])}
EOF

cat > /workspace/Shikshasamvaad/src/chatbot/crisis_detector.py << 'EOF'
CRISIS_KEYWORDS = {"hopeless", "suicide", "self-harm", "drop out", "give up", "end it", "kill myself"}

def detect_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)
EOF

cat > /workspace/Shikshasamvaad/src/chatbot/server.py << 'EOF'
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
EOF

# Rasa basic NLU examples
cat > /workspace/Shikshasamvaad/src/chatbot/rasa/nlu.yml << 'EOF'
version: "3.1"
nlu:
  - intent: greet
    examples: |
      - hello
      - hi
      - hey
  - intent: stress_check
    examples: |
      - I feel stressed
      - I'm overwhelmed
      - too much pressure
  - intent: cope_tips
    examples: |
      - tips to cope
      - how to manage stress
      - mindfulness ideas
  - intent: crisis_help
    examples: |
      - I want to give up
      - I feel hopeless
      - I want to end it
EOF

# Dashboard stubs
cat > /workspace/Shikshasamvaad/src/dashboard/visualizations.py << 'EOF'
import pandas as pd
import plotly.express as px

def risk_distribution(df: pd.DataFrame):
    return px.histogram(df, x="dropout_risk", nbins=20, title="Dropout Risk Distribution")

def attendance_vs_risk(df: pd.DataFrame):
    return px.scatter(df, x="attendance", y="dropout_risk", title="Attendance vs Dropout Risk")
EOF

cat > /workspace/Shikshasamvaad/src/dashboard/reports.py << 'EOF'
from pathlib import Path
import pandas as pd

def generate_report_csv(df: pd.DataFrame, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return str(out)

def generate_report_pdf(df: pd.DataFrame, output_path: str) -> str:
    # Placeholder: switch to reportlab/fpdf2 as needed
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        f.write("Shikshasamvaad Report (placeholder)\n")
        f.write(f"Rows: {len(df)}\n")
    return str(out)
EOF

cat > /workspace/Shikshasamvaad/src/dashboard/streamlit_app.py << 'EOF'
import streamlit as st
import pandas as pd
from pathlib import Path
from .visualizations import risk_distribution, attendance_vs_risk

st.set_page_config(page_title="Shikshasamvaad Dashboard", layout="wide")
st.title("Shikshasamvaad Wellness Dashboard")

pred_path = Path("data/processed/risk_predictions.csv")
if pred_path.exists():
    df = pd.read_csv(pred_path)
    st.success(f"Loaded predictions: {len(df)} rows")
    st.plotly_chart(risk_distribution(df), use_container_width=True)
    st.plotly_chart(attendance_vs_risk(df), use_container_width=True)
    high_risk = df[df["dropout_risk"] >= 0.7].copy()
    high_risk["anon_id"] = high_risk["student_id"].apply(lambda s: hash(s) % 100000)
    st.subheader("High-Risk Students (Anonymized)")
    st.dataframe(high_risk[["anon_id", "course", "dropout_risk", "risk_ci_lower", "risk_ci_upper"]])
else:
    st.warning("No predictions found. Generate data and run training/inference.")
EOF

# Database layer
cat > /workspace/Shikshasamvaad/src/database/sqlite_db.py << 'EOF'
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_engine(uri: str):
    return create_engine(uri, future=True)

def init_db(uri: str, schema_sql_path: str):
    engine = get_engine(uri)
    with engine.begin() as conn:
        with open(schema_sql_path, "r") as f:
            conn.execute(text(f.read()))
    return engine

def get_session(uri: str):
    engine = get_engine(uri)
    return sessionmaker(bind=engine, future=True)()
EOF

cat > /workspace/Shikshasamvaad/src/database/firebase_db.py << 'EOF'
from pathlib import Path
from typing import Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore

_app_initialized = False

def init_firebase(credentials_path: str) -> None:
    global _app_initialized
    if _app_initialized:
        return
    cred_path = Path(credentials_path)
    if not cred_path.exists():
        raise FileNotFoundError(f"Firebase credentials not found: {credentials_path}")
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)
    _app_initialized = True

def push_document(collection: str, doc: Dict[str, Any], credentials_path: Optional[str] = None) -> str:
    if not _app_initialized and credentials_path:
        init_firebase(credentials_path)
    db = firestore.client()
    ref = db.collection(collection).add(doc)
    return ref[1].id
EOF

cat > /workspace/Shikshasamvaad/src/database/schema.sql << 'EOF'
CREATE TABLE IF NOT EXISTS students (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id TEXT,
  course TEXT,
  dropout_risk REAL,
  risk_ci_lower REAL,
  risk_ci_upper REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chatbot_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id TEXT,
  message TEXT,
  sentiment_label TEXT,
  sentiment_score REAL,
  crisis BOOLEAN,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id TEXT,
  mood TEXT,
  note TEXT,
  sentiment_label TEXT,
  sentiment_score REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

# Utils
cat > /workspace/Shikshasamvaad/src/utils/logger.py << 'EOF'
from loguru import logger

def get_logger(name: str = "Shikshasamvaad"):
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level="INFO")
    return logger.bind(app=name)
EOF

cat > /workspace/Shikshasamvaad/src/utils/helpers.py << 'EOF'
import hashlib

def anonymize_id(student_id: str) -> str:
    return hashlib.sha256(student_id.encode("utf-8")).hexdigest()[:10]
EOF

cat > /workspace/Shikshasamvaad/src/utils/constants.py << 'EOF'
CRISIS_TERMS = ["hopeless", "suicide", "self-harm", "drop out", "give up", "end it"]
EOF

# Scripts
cat > /workspace/Shikshasamvaad/scripts/generate_lms_data.py << 'EOF'
import random
import pandas as pd
import datetime
from pathlib import Path

# Config
num_students = 30
num_courses = 5
students = [f"S{1000+i}" for i in range(num_students)]
courses = [f"Course_{i}" for i in range(1, num_courses+1)]

data = []
for student in students:
    for course in courses:
        attendance = random.randint(50, 100)
        submissions = random.randint(5, 10)
        grades = [random.randint(40, 100) for _ in range(submissions)]
        avg_grade = sum(grades) / len(grades)
        data.append({
            "student_id": student,
            "course": course,
            "attendance": attendance,
            "submissions": submissions,
            "avg_grade": avg_grade,
            "last_activity": datetime.date.today() - datetime.timedelta(days=random.randint(0, 15))
        })

df = pd.DataFrame(data)
out = Path("data/raw/lms_data.csv")
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f"Sample LMS data generated -> {out}")
print(df.head())
EOF

cat > /workspace/Shikshasamvaad/scripts/ingest_lms_data.py << 'EOF'
import argparse
import pandas as pd
from pathlib import Path
from src.risk_engine.preprocess import add_last_activity_days
from src.database.sqlite_db import init_db, get_engine
from src.database.firebase_db import push_document

def ingest_sqlite(df: pd.DataFrame, uri: str, schema_path: str):
    init_db(uri, schema_path)
    engine = get_engine(uri)
    df.to_sql("risk_scores", engine, if_exists="append", index=False)

def ingest_firebase(df: pd.DataFrame, credentials_path: str):
    for _, row in df.iterrows():
        push_document("risk_scores", row.to_dict(), credentials_path=credentials_path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/raw/lms_data.csv")
    ap.add_argument("--backend", choices=["sqlite","firebase"], default="sqlite")
    ap.add_argument("--sqlite_uri", default="sqlite:///data/processed/shikshasamvaad.db")
    ap.add_argument("--firebase_credentials", default="config/firebase_config.json")
    ap.add_argument("--schema", default="src/database/schema.sql")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    df = add_last_activity_days(df)
    if args.backend == "sqlite":
        ingest_sqlite(df, args.sqlite_uri, args.schema)
        print("Ingested into SQLite.")
    else:
        ingest_firebase(df, args.firebase_credentials)
        print("Ingested into Firebase.")
EOF

cat > /workspace/Shikshasamvaad/scripts/run_chatbot.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)"
python src/chatbot/server.py
EOF
chmod +x /workspace/Shikshasamvaad/scripts/run_chatbot.sh

cat > /workspace/Shikshasamvaad/scripts/run_dashboard.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)"
streamlit run src/dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
EOF
chmod +x /workspace/Shikshasamvaad/scripts/run_dashboard.sh

# Tests
cat > /workspace/Shikshasamvaad/tests/test_risk_engine.py << 'EOF'
def test_imports():
    from src.risk_engine.data_loader import load_raw_lms  # noqa:F401
    from src.risk_engine.preprocess import add_last_activity_days  # noqa:F401
    from src.risk_engine.bnn_model import SimpleBNN  # noqa:F401
EOF

cat > /workspace/Shikshasamvaad/tests/test_chatbot.py << 'EOF'
def test_crisis_detector():
    from src.chatbot.crisis_detector import detect_crisis
    assert detect_crisis("I feel hopeless") is True
    assert detect_crisis("I'm fine") is False
EOF

cat > /workspace/Shikshasamvaad/tests/test_dashboard.py << 'EOF'
def test_visualization_imports():
    from src.dashboard.visualizations import risk_distribution  # noqa:F401
EOF

cat > /workspace/Shikshasamvaad/tests/test_database.py << 'EOF'
from pathlib import Path

def test_schema_file_exists():
    assert Path("src/database/schema.sql").exists()
EOF

# Deployments
cat > /workspace/Shikshasamvaad/deployments/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV PYTHONPATH=/app
EXPOSE 5001 8501
CMD ["bash","-lc","python scripts/generate_lms_data.py && python src/risk_engine/train.py && python src/risk_engine/predict.py && streamlit run src/dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]
EOF

cat > /workspace/Shikshasamvaad/deployments/docker-compose.yml << 'EOF'
version: "3.9"
services:
  chatbot:
    build:
      context: ..
      dockerfile: deployments/Dockerfile
    command: bash -lc "python src/chatbot/server.py"
    ports:
      - "5001:5001"
    volumes:
      - ..:/app
  dashboard:
    build:
      context: ..
      dockerfile: deployments/Dockerfile
    command: bash -lc "streamlit run src/dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0"
    ports:
      - "8501:8501"
    volumes:
      - ..:/app
EOF

cat > /workspace/Shikshasamvaad/deployments/streamlit_cloud.yml << 'EOF'
app:
  name: Shikshasamvaad Dashboard
  entrypoint: src/dashboard/streamlit_app.py
  python_version: "3.11"
  commands:
    prelaunch:
      - pip install -r requirements.txt
      - python scripts/generate_lms_data.py
      - python src/risk_engine/train.py
      - python src/risk_engine/predict.py
EOF

# Initialize git
cd /workspace/Shikshasamvaad
git init
git add .
git commit -m "Initialize Shikshasamvaad skeleton: configs, src stubs, scripts, tests, deployments"