import json
from typing import Any, Dict, List
from schemas import AnswerEvaluation, WeaknessReport

def next_question(role: str, history: List[Dict[str, Any]], router, rag) -> Dict[str, Any]:
    """Agent tool 1: choose a new question using role and interview history."""
    asked = [x.get("question", "") for x in history]
    context = rag.search(f"Interview question for role: {role}", k=5)
    available = [x for x in context if x["question"] not in asked]
    if not available:
        available = context
    if available:
        candidate = available[0]
        question = candidate["question"]
        source_ids = [candidate["id"]]
    else:
        question = "Describe a challenging project relevant to this role and how you handled it."
        source_ids = []

    prompt = (
        f"Target role: {role}\nQuestions already asked: {asked}\n"
        f"Suggested question from the question bank: {question}\n"
        "Return one concise, clear interview question suitable for this role. "
        "Do not repeat a question already asked."
    )
    final_question = router.complete(
        "question",
        "You are a fair technical interviewer. Return only the question, no numbering or explanation.",
        prompt,
    ).strip().strip('"')
    return {"question": final_question or question, "source_ids": source_ids}

def score_answer(question: str, answer: str, role: str, router, rag) -> Dict[str, Any]:
    """Agent tool 2: retrieve references and score the answer against them."""
    references = rag.search(f"{role}. Question: {question}. Candidate answer: {answer}", k=3)
    ref_text = "\n\n".join(
        f"Source ID: {r['id']}\nQuestion: {r['question']}\n"
        f"Model answer: {r['model_answer']}\nKey points: {r['key_points']}"
        for r in references
    )
    prompt = f"""
Role: {role}
Interview question: {question}
Candidate answer: {answer}

Retrieved reference material (use it as guidance, not as the only possible valid answer):
{ref_text}

Evaluate fairly. Give a score from 0 to 10, list concrete strengths and missing points,
and give actionable feedback. Do not reward keywords alone. If the answer is reasonable
but different from the model answer, acknowledge that. Return valid JSON with keys:
score, strengths, missing_points, feedback, source_ids.
source_ids must contain IDs of references actually used.
"""
    raw = router.complete(
        "score",
        "You are a careful interview evaluator. Output only valid JSON matching the requested schema.",
        prompt,
    )
    try:
        data = json.loads(raw)
        evaluation = AnswerEvaluation.model_validate(data)
    except Exception:
        # One repair attempt makes model output more robust.
        repaired = router.complete(
            "score",
            "Convert the supplied text to valid JSON with keys score, strengths, missing_points, feedback, source_ids. Output JSON only.",
            raw,
        )
        data = json.loads(repaired)
        evaluation = AnswerEvaluation.model_validate(data)
    valid_ids = {r["id"] for r in references}
    evaluation.source_ids = [sid for sid in evaluation.source_ids if sid in valid_ids]
    return {"evaluation": evaluation.model_dump(), "references": references}

def summarize_weaknesses(history: List[Dict[str, Any]], router) -> Dict[str, Any]:
    """Agent tool 3: summarize recurring gaps and recommend a study plan."""
    if not history:
        return WeaknessReport(
            summary="No answers have been evaluated yet.",
            recurring_gaps=[],
            study_plan=["Complete a mock interview first."]
        ).model_dump()

    material = []
    for i, item in enumerate(history, start=1):
        ev = item.get("evaluation", {})
        material.append(
            f"Q{i}: {item.get('question')}\nScore: {ev.get('score')}\n"
            f"Missing points: {ev.get('missing_points')}\nFeedback: {ev.get('feedback')}"
        )
    raw = router.complete(
        "report",
        "You are an interview coach. Return only valid JSON.",
        "Summarize recurring skill gaps and give a practical study plan based on these evaluations:\n"
        + "\n\n".join(material)
        + "\nReturn JSON keys: summary, recurring_gaps (list), study_plan (list).",
    )
    try:
        return WeaknessReport.model_validate(json.loads(raw)).model_dump()
    except Exception:
        return WeaknessReport(
            summary="Review the feedback from each answer and focus on repeated missing points.",
            recurring_gaps=list(dict.fromkeys(
                gap for item in history
                for gap in item.get("evaluation", {}).get("missing_points", [])
            ))[:8],
            study_plan=["Review the recurring gaps listed above.", "Practice explaining each concept aloud."]
        ).model_dump()
