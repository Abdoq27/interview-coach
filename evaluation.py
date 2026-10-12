from statistics import mean, pstdev

def compare_with_humans(rows):
    """Rows: dicts containing ai_score and human_score, each on a 0-10 scale."""
    if not rows:
        return {"n": 0, "mae": None, "within_1_point_pct": None}
    errors = [abs(float(r["ai_score"]) - float(r["human_score"])) for r in rows]
    return {
        "n": len(rows),
        "mae": round(mean(errors), 3),
        "within_1_point_pct": round(100 * sum(e <= 1 for e in errors) / len(errors), 1),
    }

def consistency_report(scores):
    """Scores are repeated scores for the same answer, e.g. [7, 7.5, 7]."""
    if len(scores) < 2:
        return {"n_runs": len(scores), "mean_score": None, "std_dev": None, "range": None}
    values = [float(s) for s in scores]
    return {
        "n_runs": len(values),
        "mean_score": round(mean(values), 3),
        "std_dev": round(pstdev(values), 3),
        "range": round(max(values) - min(values), 3),
    }
