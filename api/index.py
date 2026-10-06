from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Input format sent from index.html
class AnswerSubmission(BaseModel):
    problem_id: str
    user_answer: str
    student_id: Optional[str] = "student_guest"

class HintRequest(BaseModel):
    problem_id: str
    hint_level: int

# --- API ENDPOINTS ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Axiom AI Tutor API"}

@app.post("/api/evaluate")
def evaluate_answer(data: AnswerSubmission):
    """
    Evaluates the student's submitted math answer.
    Replace/expand this function with your actual Python notebook logic.
    """
    user_ans = data.user_answer.strip().lower()
    
    # Placeholder logic (Replace with your notebook's solver/evaluator)
    is_correct = user_ans in ["5/6", "5 / 6", "0.833", "0.83"]
    
    if is_correct:
        feedback = "Excellent! You correctly identified the common denominator."
        misconception = None
    else:
        # Example misconception detection logic
        if "+" in user_ans or "2/7" in user_ans:
            misconception = "Added Denominators Directly"
            feedback = "Remember: When adding fractions, you must find a common denominator first, not add top and bottom across!"
        else:
            misconception = "Calculation Error"
            feedback = "Not quite. Check your common denominator calculations and try again."

    return {
        "correct": is_correct,
        "feedback": feedback,
        "flagged_misconception": misconception,
        "myp_criterion": "Criterion A"
    }

@app.post("/api/hint")
def generate_hint(data: HintRequest):
    """
    Generates a Socratic hint based on requested hint level.
    """
    hints = {
        1: "What is the lowest common multiple (LCM) of the denominators 2 and 3?",
        2: "Convert 1/2 and 1/3 into equivalent fractions with a denominator of 6.",
        3: "1/2 = 3/6 and 1/3 = 2/6. Now add the numerators: 3/6 + 2/6 = ?"
    }
    
    selected_hint = hints.get(data.hint_level, "Take a step back and identify what the question is asking.")
    return {"hint": selected_hint, "level": data.hint_level}
