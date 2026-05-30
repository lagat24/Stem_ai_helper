from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()


from utils.validators import validate_topic

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.ai_engine import (
    generate_question,
    evaluate_answer
)

app = Flask(__name__)

# ==========================================
# RATE LIMITER
# ==========================================

limiter = Limiter(
    get_remote_address,
    app=app
)

# ==========================================
# SESSION STATE
# ==========================================

sessions = {}

# ==========================================
# PAGES
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dash.html")


# ==========================================
# START SESSION
# ==========================================

@limiter.limit("10 per minute")
@app.route("/start", methods=["POST"])
def start():

    data = request.get_json()

    topic = data.get("topic")

    # VALIDATE TOPIC
    if not validate_topic(topic):

        return jsonify({

            "success": False,

            "message":
            "Invalid topic."

        }), 400

    session_id = data.get("session_id")

    question_data = generate_question(topic)

    sessions[session_id] = {

        "topic": topic,

        "score": 0,

        "question_number": 1,

        "current_question": question_data
    }

    return jsonify(question_data)


# ==========================================
# SUBMIT ANSWER
# ==========================================

@limiter.limit("20 per minute")
@app.route("/submit", methods=["POST"])
def submit():

    data = request.get_json()

    session_id = data.get("session_id")

    user_answer = data.get("user_answer")

    session = sessions.get(session_id)

    if not session:

        return jsonify({
            "success": False,
            "message": "Session not found."
        }), 404

    current_question = session["current_question"]

    evaluation = evaluate_answer(

        question=current_question["question"],

        correct_answer=current_question["answer"],

        explanation=current_question["explanation"],

        user_answer=user_answer
    )

    if evaluation["correct"]:
        session["score"] += 1

    return jsonify({

        "success": True,

        "correct": evaluation["correct"],

        "feedback": evaluation["feedback"],

        "score": session["score"],

        "question_number":
        session["question_number"]
    })


# ==========================================
# NEXT QUESTION
# ==========================================

@limiter.limit("10 per minute")
@app.route("/next", methods=["POST"])
def next_question():

    data = request.get_json()

    session_id = data.get("session_id")

    session = sessions.get(session_id)

    if not session:

        return jsonify({
            "success": False,
            "message": "Session not found."
        }), 404

    session["question_number"] += 1

    question_data = generate_question(
        session["topic"]
    )

    session["current_question"] = question_data

    return jsonify({

        "success": True,

        "question":
        question_data["question"],

        "answer":
        question_data["answer"],

        "explanation":
        question_data["explanation"],

        "question_number":
        session["question_number"],

        "score":
        session["score"]
    })


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    app.run(debug=True, port=8080)
