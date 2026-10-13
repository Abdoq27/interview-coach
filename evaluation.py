
from statistics import mean, pstdev
from time import perf_counter


def compare_with_humans(rows):
    """Compare AI scores with human scores on a 0-10 scale."""
    if not rows:
        return {
            "n": 0,
            "mae": None,
            "within_1_point_pct": None,
        }

    errors = [
        abs(float(r["ai_score"]) - float(r["human_score"]))
        for r in rows
    ]

    return {
        "n": len(errors),
        "mae": round(mean(errors), 3),
        "within_1_point_pct": round(
            100 * sum(e <= 1 for e in errors) / len(errors), 1
        ),
    }


def consistency_report(scores):
    """Measure consistency across repeated scores."""
    if not scores:
        return {
            "n_runs": 0,
            "mean_score": None,
            "std_dev": None,
            "range": None,
        }

    values = [float(s) for s in scores]

    if len(values) < 2:
        return {
            "n_runs": len(values),
            "mean_score": round(mean(values), 3),
            "std_dev": None,
            "range": 0.0,
        }

    return {
        "n_runs": len(values),
        "mean_score": round(mean(values), 3),
        "std_dev": round(pstdev(values), 3),
        "range": round(max(values) - min(values), 3),
    }


def retrieval_metrics(results, expected_ids, k=3):
    """Measure retrieval quality using known relevant record IDs."""
    retrieved_ids = [item["id"] for item in results[:k]]
    expected = set(expected_ids)

    if not expected:
        return {
            "precision_at_k": None,
            "recall_at_k": None,
            "hit_at_k": None,
        }

    relevant_found = sum(
        1 for item_id in retrieved_ids if item_id in expected
    )

    return {
        "precision_at_k": round(
            relevant_found / max(1, len(retrieved_ids)), 3
        ),
        "recall_at_k": round(
            relevant_found / len(expected), 3
        ),
        "hit_at_k": int(relevant_found > 0),
    }


def measure_latency(function, *args, **kwargs):
    """Run a function and return its result and elapsed time in seconds."""
    start = perf_counter()
    result = function(*args, **kwargs)
    elapsed = perf_counter() - start

    return {
        "result": result,
        "latency_seconds": round(elapsed, 3),
    }
