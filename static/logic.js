// ======================================
// STEM AI HELPER
// FRONTEND LOGIC
// ======================================


// ======================================
// SESSION STATE
// ======================================

let sessionId = "";

let currentTopic = "";

let currentQuestion = null;

let score = 0;

let questionNumber = 0;

let totalQuestions = 10;

let sessionStarted = false;


// ======================================
// DOM ELEMENTS
// ======================================

const topicInput =
document.getElementById("topic");

const questionText =
document.getElementById("questionText");

const answerInput =
document.getElementById("useranswer");

const feedbackBox =
document.getElementById("feedbackbox");

const questionCounter =
document.getElementById("questionCounter");

const scoreCounter =
document.getElementById("scoreCounter");

const explainBtn =
document.getElementById("explainBtn");


// Disable answer box until session starts
answerInput.disabled = true;


// ======================================
// START SESSION
// ======================================

async function startSession() {

    // New session every time Start is pressed
    sessionId = Date.now().toString();

    explainBtn.disabled = true;

    const topic =
    topicInput.value.trim();

    if (topic === "") {

        feedbackBox.innerHTML =
        "Please enter a topic first.";

        return;
    }

    sessionStarted = true;

    currentTopic = topic;

    score = 0;

    questionNumber = 1;

    updateStats();

    feedbackBox.innerHTML =
    "Generating question...";

    answerInput.value = "";

    try {

        const response = await fetch("/start", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                topic: currentTopic,

                session_id: sessionId
            })
        });

        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );
        }

        const data =
        await response.json();

        if (!data.question) {

            throw new Error(
                "Invalid response from server."
            );
        }

        currentQuestion = data;

        renderQuestion();

        feedbackBox.innerHTML =
        "Question generated successfully.";

    } catch (error) {

        console.error(error);

        feedbackBox.innerHTML =
        "Unable to start session.";
    }
}


// ======================================
// RENDER QUESTION
// ======================================

function renderQuestion() {

    if (!currentQuestion) {

        questionText.innerHTML =
        "No question available.";

        return;
    }

    questionText.innerHTML =
    currentQuestion.question;

    answerInput.disabled = false;
}


// ======================================
// SUBMIT ANSWER
// ======================================

async function submitAnswer() {

    const submitButton =
    document.querySelector(
        'button[onclick="submitAnswer()"]'
    );

    submitButton.disabled = true;

    if (!sessionStarted) {

        feedbackBox.innerHTML =
        "Start a session first.";

        return;
    }

    const userAnswer =
    answerInput.value.trim();

    if (userAnswer === "") {

        feedbackBox.innerHTML =
        "Please enter an answer.";

        return;
    }

    feedbackBox.innerHTML =
    "Checking answer...";

    try {

        const response = await fetch("/submit", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                session_id: sessionId,

                user_answer: userAnswer
            })
        });

        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );
        }

        const data =
        await response.json();

        if (!data.success) {

            throw new Error(
                data.message ||
                "Answer evaluation failed."
            );
        }

        submitButton.disabled = false;

        feedbackBox.innerHTML =
        data.feedback;

        score = data.score;

        updateStats();

        explainBtn.disabled = false;

    } catch (error) {

        console.error(error);

        submitButton.disabled = false;

        feedbackBox.innerHTML =
        "Unable to evaluate answer.";
    }
}


// ======================================
// EXPLAIN ANSWER
// ======================================

function explainAnswer() {

    if (!currentQuestion) {

        feedbackBox.innerHTML =
        "No active question.";

        return;
    }

    feedbackBox.innerHTML =
    `
    <strong>Explanation:</strong>
    <br><br>

    ${currentQuestion.explanation}
    `;
}


// ======================================
// NEXT QUESTION
// ======================================

async function nextQuestion() {

    if (!sessionStarted) {

        feedbackBox.innerHTML =
        "Start a session first.";

        return;
    }

    if (questionNumber >= totalQuestions) {

        questionText.innerHTML =
        "🎉 Session Complete";

        feedbackBox.innerHTML =
        `Final Score: ${score}/${totalQuestions}`;

        answerInput.disabled = true;

        explainBtn.disabled = true;

        return;
    }

    feedbackBox.innerHTML =
    "Generating next question...";

    answerInput.value = "";

    explainBtn.disabled = true;

    try {

        const response = await fetch("/next", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                session_id: sessionId
            })
        });

        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );
        }

        const data =
        await response.json();

        if (!data.success) {

            throw new Error(
                data.message ||
                "Unable to generate question."
            );
        }

        currentQuestion = {

            question: data.question,

            answer: data.answer,

            explanation: data.explanation
        };

        questionNumber =
        data.question_number;

        score =
        data.score;

        updateStats();

        renderQuestion();

        feedbackBox.innerHTML =
        "New question generated.";

    } catch (error) {

        console.error(error);

        feedbackBox.innerHTML =
        "Unable to load next question.";
    }
}


// ======================================
// UPDATE STATS
// ======================================

function updateStats() {

    questionCounter.innerHTML =
    `${questionNumber} / ${totalQuestions}`;

    scoreCounter.innerHTML =
    score;
}