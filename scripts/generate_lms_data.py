import random
import pandas as pd
import datetime
from pathlib import Path
import json

# Config
num_students = 30
num_courses = 5
students = [f"S{1000+i}" for i in range(num_students)]
course_codes = [f"CSE{i:03d}" for i in range(101, 101 + num_courses)]
course_names = [f"Course_{i}" for i in range(1, num_courses+1)]

# Define attribute space and sample weights per course
attribute_keys = [
    "problem_solving", "logical_reasoning", "retention", "communication", "collaboration"
]
def random_attr_weights():
    weights = {k: round(random.uniform(0.3, 1.0), 2) for k in attribute_keys}
    s = sum(weights.values())
    # normalize roughly
    return {k: round(v / s, 2) for k, v in weights.items()}

# Build courses table-like data
courses = []
for code, name in zip(course_codes, course_names):
    courses.append({
        "course_code": code,
        "name": name,
        "attributes_json": json.dumps(random_attr_weights()),
        "created_at": datetime.date.today()
    })

# Assessments timeline per course/student
assessment_types = ["internal", "assignment", "quiz", "midterm", "internal", "assignment", "quiz", "final"]
start_date = datetime.date.today() - datetime.timedelta(days=120)

assessments = []
submissions = []
attendance_records = []

for student in students:
    for code in course_codes:
        # Attendance: 60-100% uniformly, 40-60 sessions
        total_sessions = random.randint(40, 60)
        attended_sessions = 0
        for i in range(total_sessions):
            day = start_date + datetime.timedelta(days=i*2)
            present = random.random() < random.uniform(0.6, 0.98)
            attended_sessions += 1 if present else 0
            attendance_records.append({
                "student_id": student,
                "course_code": code,
                "date": day,
                "present": present
            })

        # Rolling assessments
        prev_score = None
        for idx, a_type in enumerate(assessment_types, start=1):
            due_date = start_date + datetime.timedelta(days=idx*14)
            submitted_at = due_date + datetime.timedelta(days=random.choice([-1, 0, 0, 0, 1]))
            max_score = 100
            score = random.randint(40, 100)
            assessments.append({
                "student_id": student,
                "course_code": code,
                "assessment_type": a_type,
                "assessment_name": f"{a_type.title()} {idx}",
                "due_date": due_date,
                "submitted_at": submitted_at,
                "max_score": max_score,
                "score": score
            })
            # Submission improvement
            score_delta = (score - prev_score) if prev_score is not None else 0
            prev_score = score
            submissions.append({
                "student_id": student,
                "course_code": code,
                "assessment_id": None,  # will be null in CSV; DB can link during ingestion if needed
                "submitted_at": submitted_at,
                "on_time": submitted_at <= due_date,
                "score_delta": score_delta,
                "notes": ""
            })

# Aggregated per-course per-student summary compatible with previous pipeline
summary_rows = []
for student in students:
    for code, name in zip(course_codes, course_names):
        att_df = pd.DataFrame([r for r in attendance_records if r["student_id"] == student and r["course_code"] == code])
        present_pct = 100.0 * att_df["present"].mean() if not att_df.empty else 0.0
        scores = [a["score"] for a in assessments if a["student_id"] == student and a["course_code"] == code]
        submissions_count = len(scores)
        avg_grade = sum(scores)/len(scores) if scores else 0
        last_activity = max([r["submitted_at"] for r in submissions if r["student_id"] == student and r["course_code"] == code], default=datetime.date.today())
        summary_rows.append({
            "student_id": student,
            "course": name,
            "course_code": code,
            "attendance": round(present_pct),
            "submissions": submissions_count,
            "avg_grade": avg_grade,
            "last_activity": last_activity
        })

raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

pd.DataFrame(summary_rows).to_csv(raw_dir / "lms_data.csv", index=False)
pd.DataFrame(courses).to_csv(raw_dir / "courses.csv", index=False)
pd.DataFrame(assessments).to_csv(raw_dir / "assessments.csv", index=False)
pd.DataFrame(submissions).to_csv(raw_dir / "submissions.csv", index=False)
pd.DataFrame(attendance_records).to_csv(raw_dir / "attendance.csv", index=False)

print("Generated datasets:")
for f in ["lms_data.csv", "courses.csv", "assessments.csv", "submissions.csv", "attendance.csv"]:
    p = raw_dir / f
    print(f" - {p} ({p.stat().st_size} bytes)")