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