"""
planner.py — Generate a day-by-day study plan from remaining topics + exam date.
Uses Gemini API when available; falls back to a smart rule-based scheduler.
"""

import re
import json
from datetime import date, timedelta


def generate_plan(
    remaining_topics: list[str],
    exam_date: date,
    hours_per_day: float,
    subject: str,
    api_key: str = "",
    model: str = "gemini-1.5-flash",
) -> list[dict]:
    """
    Returns a list of day-plan dicts:
    [
      {
        "date": "2026-05-28",
        "day": "Wednesday",
        "topics": ["Topic A", "Topic B"],
        "hours": 3,
        "type": "study"   # or "revision" / "buffer"
      },
      ...
    ]
    """
    today = date.today()
    days_available = (exam_date - today).days

    if not remaining_topics:
        return []

    if api_key:
        try:
            return _llm_plan(remaining_topics, exam_date, hours_per_day, subject, api_key, model, days_available)
        except Exception:
            pass

    return _rule_based_plan(remaining_topics, exam_date, hours_per_day, days_available)


# ── Rule-based scheduler ──────────────────────────────────────────────────────

def _rule_based_plan(
    topics: list[str],
    exam_date: date,
    hours_per_day: float,
    days_available: int,
) -> list[dict]:
    today = date.today()

    # Estimate time per topic based on complexity
    def topic_hours(t):
        words = len(t.split())
        if words <= 3:
            return 0.5
        elif words <= 6:
            return 1.0
        else:
            return 1.5

    topic_times = [(t, topic_hours(t)) for t in topics]
    total_hours_needed = sum(h for _, h in topic_times)

    # Calculate usable study days (leave 1 revision day if possible)
    study_days = max(1, days_available - 1) if days_available > 2 else max(1, days_available)
    revision_day = days_available > 2

    # Auto-scale hours if not enough time
    effective_hours = max(hours_per_day, total_hours_needed / study_days)

    plan = []
    current_day = today
    day_topics = []
    day_hours = 0.0

    for topic, t_hours in topic_times:
        if day_hours + t_hours > effective_hours and day_topics:
            if current_day <= exam_date:
                plan.append(_make_day(current_day, day_topics, day_hours, "study"))
                current_day += timedelta(days=1)
            day_topics = []
            day_hours = 0.0

        day_topics.append(topic)
        day_hours += t_hours

    # Flush last study day
    if day_topics and current_day <= exam_date:
        plan.append(_make_day(current_day, day_topics, day_hours, "study"))
        current_day += timedelta(days=1)

    # Revision day
    if revision_day and current_day <= exam_date:
        plan.append(_make_day(current_day, ["📖 Revise all topics", "Practice questions", "Summary notes"], hours_per_day, "revision"))
        current_day += timedelta(days=1)

    # Buffer / exam day
    if current_day <= exam_date:
        plan.append(_make_day(exam_date, ["🎯 Final revision", "Stay calm, you've got this!"], 1.0, "buffer"))

    return plan


def _make_day(d: date, topics: list[str], hours: float, dtype: str) -> dict:
    return {
        "date": d.strftime("%Y-%m-%d"),
        "day": d.strftime("%A"),
        "topics": topics,
        "hours": round(hours, 1),
        "type": dtype,
    }


# ── LLM-based planner ─────────────────────────────────────────────────────────

def _llm_plan(
    topics: list[str],
    exam_date: date,
    hours_per_day: float,
    subject: str,
    api_key: str,
    model: str,
    days_available: int,
) -> list[dict]:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)

    today = date.today()
    topic_list = "\n".join(f"- {t}" for t in topics)

    prompt = f"""
You are an academic study planner. Create a realistic day-by-day study schedule.

Subject: {subject}
Start date: {today.strftime("%Y-%m-%d")}
Exam date: {exam_date.strftime("%Y-%m-%d")}
Study hours per day: {hours_per_day}
Days available: {days_available}

Topics to cover:
{topic_list}

Rules:
- Distribute topics evenly across available days
- Add a revision day before the exam if possible
- Group related topics together on the same day
- On the last day (exam day) only put "Final revision"
- Return ONLY a JSON array, no markdown, no explanation

Return format:
[
  {{
    "date": "YYYY-MM-DD",
    "day": "Monday",
    "topics": ["Topic A", "Topic B"],
    "hours": 3.0,
    "type": "study"
  }}
]
type must be one of: "study", "revision", "buffer"
"""
    resp = m.generate_content(prompt)
    raw = resp.text.strip()
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
    plan = json.loads(raw)
    if not isinstance(plan, list):
        raise ValueError("LLM returned non-list plan")
    return plan