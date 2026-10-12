import os
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from llm_router import LLMRouter
from rag import InterviewRAG
from agent import InterviewAgent
from evaluation import compare_with_humans, consistency_report

load_dotenv()
st.set_page_config(page_title="Interview Coach", page_icon="🎤", layout="wide")

st.markdown("""
<style>
.main {background: #fbfbfe;}
.block-container {padding-top: 2rem; max-width: 1150px;}
.hero {padding: 1.2rem 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#24233f,#3e426f); color: white;}
.hero h1 {color:white; margin:0;}
.hero p {color:#e5e7f5; margin-bottom:0;}
div.stButton > button[kind="primary"] {background:#0d9488; border-color:#0d9488;}
</style>
<div class="hero">
<h1>🎤 Interview Coach</h1>
<p>Practice a mock interview, get structured feedback, and discover what to improve.</p>
</div>
""", unsafe_allow_html=True)

def get_services():
    if "router" not in st.session_state:
        st.session_state.router = LLMRouter()
        st.session_state.rag = InterviewRAG()
        st.session_state.agent = InterviewAgent(st.session_state.router, st.session_state.rag)
    return st.session_state.router, st.session_state.rag, st.session_state.agent

def reset_interview():
    for key in ["history", "current_question", "report", "agent_trace", "started", "role"]:
        st.session_state.pop(key, None)

with st.sidebar:
    st.header("Interview setup")
    role = st.text_input("Target role", value="Machine Learning Engineer")
    number_questions = st.select_slider("Number of questions", options=[3, 5, 7], value=5)
    st.caption("The app uses Qwen through Ollama; no OpenAI API key is needed.")
    if st.button("Reset interview"):
        reset_interview()
        st.rerun()
    st.divider()
    st.subheader("Project status")
    st.write("**RAG:** local Chroma database + Ollama embeddings")
    st.write("**Agent tools:** 3")
    st.write("**UI:** Streamlit (local)")

tab_interview, tab_report, tab_eval, tab_about = st.tabs(
    ["🎙️ Mock Interview", "📊 Weakness Report", "🧪 Evaluation", "ℹ️ How it works"]
)

with tab_interview:
    st.subheader("1. Paste the job description")
    jd = st.text_area(
        "Job description",
        placeholder="Paste the job description here...",
        height=140,
        key="job_description",
    )
    if st.button("Prepare interview", type="primary"):
        if not jd.strip():
            st.warning("Paste a job description first.")
        else:
            router, rag, agent = get_services()
            with st.spinner("Preparing the question bank..."):
                indexed = rag.index_bank()
                st.session_state.role = role.strip() or "Candidate"
                st.session_state.history = []
                st.session_state.question_limit = number_questions
                st.session_state.jd = jd.strip()
                st.session_state.started = True
                st.session_state.report = None
                st.session_state.current_question = agent.get_next_question(
                    st.session_state.role, st.session_state.history
                )
                st.success(f"Interview ready. {indexed} knowledge-bank records indexed.")
                st.rerun()

    if st.session_state.get("started"):
        history = st.session_state.get("history", [])
        limit = st.session_state.get("question_limit", 5)
        st.divider()
        st.progress(min(len(history) / limit, 1.0), text=f"Completed {len(history)} of {limit} answers")
        if len(history) < limit:
            question_obj = st.session_state.current_question
            st.markdown(f"### Question {len(history) + 1} of {limit}")
            st.info(question_obj["question"])
            answer_key = f"answer_{len(history)}"
            answer = st.text_area("Your answer", key=answer_key, height=160,
                                  placeholder="Explain your reasoning and include an example if possible...")
            if st.button("Submit answer and score it", type="primary", key=f"submit_{len(history)}"):
                if not answer.strip():
                    st.warning("Write an answer before submitting.")
                else:
                    router, rag, agent = get_services()
                    with st.spinner("Scoring your answer using retrieved reference material..."):
                        result = agent.evaluate(st.session_state.role, question_obj["question"], answer.strip())
                    history.append({
                        "question": question_obj["question"],
                        "answer": answer.strip(),
                        "evaluation": result["evaluation"],
                        "references": result["references"],
                    })
                    st.session_state.history = history
                    st.session_state.last_result = result
                    if len(history) < limit:
                        st.session_state.current_question = agent.get_next_question(
                            st.session_state.role, history
                        )
                    else:
                        st.session_state.report = agent.report(history)
                    st.rerun()
        else:
            st.success("Interview complete! Open the Weakness Report tab for your summary.")

        if st.session_state.get("last_result"):
            last = st.session_state.last_result
            ev = last["evaluation"]
            st.markdown("#### Latest score")
            st.metric("Score", f"{ev['score']:.1f} / 10")
            st.write("**Feedback:**", ev["feedback"])
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Strengths**")
                for x in ev["strengths"]:
                    st.write(f"- {x}")
            with c2:
                st.write("**Missing points**")
                for x in ev["missing_points"]:
                    st.write(f"- {x}")
            with st.expander("Retrieved sources / citations"):
                if last["references"]:
                    for ref in last["references"]:
                        st.markdown(f"**{ref['id']} — {ref['topic']}**")
                        st.write(ref["question"])
                        st.caption(ref["source"])
                else:
                    st.write("No reference records were retrieved.")
        with st.expander("Agent tool trace"):
            agent_trace = getattr(st.session_state.get("agent"), "trace", [])
            if agent_trace:
                st.json(agent_trace)
            else:
                st.write("Tool trace will appear after the agent runs.")

with tab_report:
    st.subheader("Weakness report")
    history = st.session_state.get("history", [])
    if not history:
        st.info("Complete at least one answer to see feedback here.")
    else:
        scores = [x["evaluation"]["score"] for x in history]
        st.metric("Average score", f"{sum(scores) / len(scores):.1f} / 10")
        report = st.session_state.get("report")
        if report:
            st.write(report["summary"])
            st.markdown("#### Recurring gaps")
            for gap in report["recurring_gaps"]:
                st.write(f"- {gap}")
            st.markdown("#### Suggested study plan")
            for item in report["study_plan"]:
                st.write(f"- {item}")
        st.markdown("#### Answer-by-answer results")
        table = pd.DataFrame([
            {"Question": x["question"], "Score / 10": x["evaluation"]["score"],
             "Missing points": "; ".join(x["evaluation"]["missing_points"])}
            for x in history
        ])
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.download_button("Download interview results (CSV)", table.to_csv(index=False).encode("utf-8-sig"),
                           file_name="interview_results.csv", mime="text/csv")

with tab_eval:
    st.subheader("Evaluation dashboard")
    st.write("The project rubric requires human comparison on 20 answers and repeated scoring of the same answer 3 times.")
    st.warning("Use real human ratings and actual model runs. Do not report placeholder numbers as experimental results.")
    st.markdown("#### Compare AI scores with human scores")
    st.caption("Enter one row per answer. Score range: 0–10.")
    sample = pd.DataFrame([{"ai_score": 7.0, "human_score": 8.0}])
    human_df = st.data_editor(sample, num_rows="dynamic", use_container_width=True, key="human_eval")
    if st.button("Calculate human comparison"):
        try:
            rows = human_df.dropna().to_dict("records")
            metrics = compare_with_humans(rows)
            st.json(metrics)
            st.caption("MAE = mean absolute error. For the final project, collect 20 human-rated answers.")
        except Exception as e:
            st.error(f"Check that both columns contain numbers from 0 to 10. Details: {e}")
    st.divider()
    st.markdown("#### Consistency: same answer scored 3 times")
    scores_text = st.text_input("Enter the three actual scores, comma-separated", value="7, 7.5, 7")
    if st.button("Calculate consistency"):
        try:
            scores = [float(x.strip()) for x in scores_text.split(",") if x.strip()]
            if len(scores) != 3 or any(s < 0 or s > 10 for s in scores):
                st.error("Enter exactly 3 scores between 0 and 10.")
            else:
                st.json(consistency_report(scores))
                st.caption("For your final report, replace these example input values with results from 3 real model runs.")
        except ValueError:
            st.error("Use numbers separated by commas.")

with tab_about:
    st.subheader("How the required components are implemented")
    st.markdown("""
    - **LLM + cost-aware router:** `llm_router.py` selects a fast model for question generation and a stronger model for scoring/reporting.
    - **Structured prompting:** `schemas.py` defines Pydantic output schemas for evaluation and the weakness report.
    - **RAG:** `rag.py` embeds the local question bank, stores vectors in Chroma, retrieves relevant records, and displays source IDs.
    - **Agent:** `agent.py` invokes three explicit tools: `next_question`, `score_answer`, and `summarize_weaknesses`. Tool activity is shown in the trace.
    - **Session state:** Streamlit session state holds the current role, interview history, and current question.
    - **Evaluation:** `evaluation.py` calculates MAE and consistency metrics from real scores.

    **Important:** This is a student project starter, not a validated hiring decision system. Treat scores as coaching feedback, not as a decision about a person's employability.
    """)

st.caption("Interview Coach • Local demo • No deployment required")
