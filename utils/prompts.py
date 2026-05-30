QUESTION_PROMPT = """
You are an expert STEM tutor.

Generate ONE educational practice question.

TOPIC:
{topic}

RULES:
- Return ONLY valid JSON
- No markdown
- No extra commentary
- Question must test understanding
- Keep answer concise

FORMAT:

{{
    "question": "...",
    "answer": "...",
    "explanation": "..."
}}
"""


EVALUATION_PROMPT = """
You are an educational evaluator.

QUESTION:
{question}

CORRECT ANSWER:
{correct_answer}

USER ANSWER:
{user_answer}

EXPLANATION:
{explanation}

Evaluate the user's answer.

Return ONLY valid JSON.

FORMAT:

{{
    "correct": true,
    "feedback": "..."
}}
"""