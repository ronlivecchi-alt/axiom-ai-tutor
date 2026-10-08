import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client

# 1. Initialize FastAPI app FIRST
app = FastAPI()

# 2. Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")

supabase: Client = None
if url and key:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"Supabase init error: {e}")

# Data Models
class StudentSubmission(BaseModel):
    student_id: str
    question_id: str
    user_answer: str

# 3. Define Routes AFTER app is defined
@app.get("/api")
@app.get("/api/")
def api_root():
    return {"message": "Axiom AI Tutor API is live!"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Axiom AI Tutor API"}

@app.post("/api/evaluate")
async def evaluate_submission(submission: StudentSubmission):
    # Place evaluation logic here
    is_correct = "x = 5" in submission.user_answer.lower() or "5" in submission.user_answer
    feedback = "Great job! That is correct." if is_correct else "Check your algebraic steps again."
    misconception_tag = None if is_correct else "Sign Error"

    if supabase:
        try:
            supabase.table("student_submissions").insert({
                "student_id": submission.student_id,
                "question_id": submission.question_id,
                "user_answer": submission.user_answer,
                "is_correct": is_correct,
                "misconception_tag": misconception_tag
            }).execute()
        except Exception as e:
            print(f"DB Insert Error: {e}")

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "misconception_tag": misconception_tag
    }

@app.get("/api/metrics")
async def get_teacher_metrics():
    if not supabase:
        return {"total_submissions": 0, "class_accuracy": 0, "top_misconceptions": []}

    try:
        response = supabase.table("student_submissions").select("*").execute()
        data = response.data or []

        total = len(data)
        if total == 0:
            return {"total_submissions": 0, "class_accuracy": 0, "top_misconceptions": []}

        correct_count = sum(1 for row in data if row.get("is_correct"))
        accuracy = round((correct_count / total) * 100, 1)

        misconception_counts = {}
        for row in data:
            tag = row.get("misconception_tag")
            if tag:
                misconception_counts[tag] = misconception_counts.get(tag, 0) + 1

        top_misconceptions = [
            {"tag": tag, "count": count}
            for tag, count in sorted(misconception_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return {
            "total_submissions": total,
            "class_accuracy": accuracy,
            "top_misconceptions": top_misconceptions
        }
    except Exception as e:
        print(f"Metrics Fetch Error: {e}")
        return {"total_submissions": 0, "class_accuracy": 0, "top_misconceptions": []}