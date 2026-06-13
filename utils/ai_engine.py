import os
import json
import re

import google.generativeai as genai

from utils.prompts import (
    QUESTION_PROMPT,
    EVALUATION_PROMPT
)

# ==========================================
# CONFIGURE GEMINI
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )

genai.configure(
    api_key=api_key
)

model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

# ==========================================
# CLEAN AI RESPONSE
# ==========================================

def extract_json(text):

    match = re.search(
        r'\{.*\}',
        text,
        re.DOTALL
    )

    if not match:

        raise ValueError(
            "No valid JSON found."
        )

    return match.group(0)

# ==========================================
# GENERATE QUESTION
# ==========================================

def generate_question(topic):

    prompt = QUESTION_PROMPT.format(
        topic=topic
    )

    # Retry AI generation 3 times
    for attempt in range(3):

        try:

            response = model.generate_content(
                prompt
            )

            cleaned = extract_json(
                response.text
            )

            return json.loads(cleaned)

        except Exception as error:

            print(
                f"Question generation attempt {attempt + 1} failed:",
                error
            )

    # Fallback response
    return {

        "question":
        "Unable to generate question.",

        "answer":
        "N/A",

        "explanation":
        "The AI service is temporarily unavailable."
    }

# ==========================================
# EVALUATE ANSWER
# ==========================================

def evaluate_answer(
    question,
    correct_answer,
    explanation,
    user_answer
):

    prompt = EVALUATION_PROMPT.format(

        question=question,

        correct_answer=correct_answer,

        explanation=explanation,

        user_answer=user_answer
    )

    # Retry AI evaluation 3 times
    for attempt in range(3):

        try:

            response = model.generate_content(
                prompt
            )

            cleaned = extract_json(
                response.text
            )

            return json.loads(cleaned)

        except Exception as error:

            print(
                f"Answer evaluation attempt {attempt + 1} failed:",
                error
            )

    # Fallback response
    return {

        "correct": False,

        "feedback":
        "Unable to evaluate answer right now. Please try again."
    }
