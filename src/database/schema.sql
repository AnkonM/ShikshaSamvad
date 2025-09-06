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