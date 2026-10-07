@app.get("/api")
@app.get("/api/")
def api_root():
    return {"message": "Axiom AI Tutor API is live!"}
import os
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

def get_db_connection():
    # Supabase / Vercel provides POSTGRES_URL or DATABASE_URL
    db_url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
    return psycopg2.connect(db_url)

class EvaluationRequest(BaseModel):
    student_id: str
    question_id: str
    user_answer: str

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Axiom AI Tutor API"}

@app.post("/api/evaluate")
def evaluate_answer(req: EvaluationRequest):
    # Place your AI grading logic here
    is_correct = req.user_answer.strip() == "42"
    misconception = None if is_correct else "Arithmetic error"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO student_submissions (student_id, question_id, user_answer, is_correct, misconception_tag)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (req.student_id, req.question_id, req.user_answer, is_correct, misconception)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {
        "is_correct": is_correct,
        "misconception_tag": misconception,
        "feedback": "Great job!" if is_correct else "Check your calculations."
    }

@app.get("/api/metrics")
def get_teacher_metrics():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*), COUNT(*) FILTER (WHERE is_correct = TRUE) FROM student_submissions;")
    total, correct = cur.fetchone()
    accuracy = round((correct / total * 100), 1) if total > 0 else 0

    cur.execute("""
        SELECT misconception_tag, COUNT(*) as count 
        FROM student_submissions 
        WHERE misconception_tag IS NOT NULL 
        GROUP BY misconception_tag 
        ORDER BY count DESC 
        LIMIT 3;
    """)
    top_misconceptions = [{"tag": row[0], "count": row[1]} for row in cur.fetchall()]

    cur.close()
    conn.close()

    return {
        "total_submissions": total,
        "class_accuracy": accuracy,
        "top_misconceptions": top_misconceptions
    }
