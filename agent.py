from tools import next_question, score_answer, summarize_weaknesses

class InterviewAgent:
    """A transparent, lightweight tool-using agent with visible trace."""
    def __init__(self, router, rag):
        self.router = router
        self.rag = rag
        self.trace = []

    def get_next_question(self, role, history):
        self.trace.append({"tool": "next_question", "status": "running"})
        result = next_question(role, history, self.router, self.rag)
        self.trace[-1]["status"] = "completed"
        self.trace[-1]["result"] = result["question"]
        return result

    def evaluate(self, role, question, answer):
        self.trace.append({"tool": "score_answer", "status": "running"})
        result = score_answer(question, answer, role, self.router, self.rag)
        self.trace[-1]["status"] = "completed"
        self.trace[-1]["result"] = f"score={result['evaluation']['score']}"
        return result

    def report(self, history):
        self.trace.append({"tool": "summarize_weaknesses", "status": "running"})
        result = summarize_weaknesses(history, self.router)
        self.trace[-1]["status"] = "completed"
        self.trace[-1]["result"] = "Weakness report generated"
        return result
