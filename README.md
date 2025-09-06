# ShikshaSamvad
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
