from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timezone
import uuid
import json
import os
import re

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

LOG_FILE = "audit_log.jsonl"


def sentence_length_variation_score(text):
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 2:
        return 0.5

    lengths = [len(sentence.split()) for sentence in sentences]
    average = sum(lengths) / len(lengths)

    if average == 0:
        return 0.5

    variance = sum((length - average) ** 2 for length in lengths) / len(lengths)
    normalized_variation = min(variance / 50, 1)

    ai_like_score = 1 - normalized_variation

    return round(ai_like_score, 2)


def vocabulary_diversity_score(text):
    words = re.findall(r"\b[a-zA-Z']+\b", text.lower())

    if len(words) < 10:
        return 0.5

    ai_markers = [
        "it is important to note",
        "it is essential",
        "furthermore",
        "moreover",
        "therefore",
        "in conclusion",
        "transformative",
        "paradigm shift",
        "stakeholders",
        "responsible deployment",
        "ethical implications",
        "various sectors",
        "numerous",
        "essential to consider"
    ]

    text_lower = text.lower()
    marker_count = sum(1 for marker in ai_markers if marker in text_lower)

    formal_words = [
        "represents",
        "transformative",
        "essential",
        "implications",
        "stakeholders",
        "collaborate",
        "deployment",
        "fundamental",
        "consequences",
        "valuations",
        "extensively"
    ]

    formal_count = sum(1 for word in words if word in formal_words)

    marker_score = min(marker_count / 4, 1)
    formal_score = min(formal_count / 8, 1)

    ai_like_score = (marker_score * 0.7) + (formal_score * 0.3)

    return round(ai_like_score, 2)


def calculate_confidence(sentence_score, vocab_score):
    confidence = (sentence_score * 0.3) + (vocab_score * 0.7)
    return round(confidence, 2)


def classify_from_score(score):
    if score >= 0.7:
        return "likely_ai"
    elif score <= 0.39:
        return "likely_human"
    else:
        return "uncertain"


def label_from_attribution(attribution):
    if attribution == "likely_ai":
        return (
            "Likely AI-Assisted\n\n"
            "This text shows several patterns commonly associated with AI-generated writing. "
            "This result is not proof of AI use, but the system has high confidence based on the available signals."
        )

    if attribution == "likely_human":
        return (
            "Likely Human-Written\n\n"
            "This text shows patterns commonly associated with human writing. "
            "This result is not proof, but the system found low evidence of AI-generated writing."
        )

    return (
        "Uncertain\n\n"
        "The system found mixed signals. Some patterns may look AI-assisted, while others may look human-written. "
        "This result should not be used as proof without human review."
    )


def write_log(entry):
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def get_log():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        entries = [json.loads(line) for line in file if line.strip()]

    return entries[-10:]


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Provenance Guard API is running"
    })


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text:
        return jsonify({"error": "Missing required field: text"}), 400

    if not creator_id:
        return jsonify({"error": "Missing required field: creator_id"}), 400

    content_id = str(uuid.uuid4())

    sentence_score = sentence_length_variation_score(text)
    vocab_score = vocabulary_diversity_score(text)
    confidence = calculate_confidence(sentence_score, vocab_score)

    attribution = classify_from_score(confidence)
    label = label_from_attribution(attribution)

    log_entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": attribution,
        "confidence": confidence,
        "sentence_variation_score": sentence_score,
        "vocabulary_diversity_score": vocab_score,
        "label": label,
        "appeal_filed": False,
        "status": "classified",
        "event_type": "submission_classified"
    }

    write_log(log_entry)

    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "appeal_filed": False,
        "status": "classified",
        "signals": {
            "sentence_variation_score": sentence_score,
            "vocabulary_diversity_score": vocab_score
        }
    })


@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    content_id = data.get("content_id")
    creator_reasoning = data.get("creator_reasoning")

    if not content_id:
        return jsonify({"error": "Missing required field: content_id"}), 400

    if not creator_reasoning:
        return jsonify({"error": "Missing required field: creator_reasoning"}), 400

    appeal_entry = {
        "content_id": content_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "under_review",
        "appeal_filed": True,
        "appeal_reasoning": creator_reasoning,
        "event_type": "appeal_submitted"
    }

    write_log(appeal_entry)

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "appeal_filed": True,
        "message": "Appeal received and logged."
    })


@app.route("/log", methods=["GET"])
def log():
    return jsonify({
        "entries": get_log()
    })


if __name__ == "__main__":
    app.run(debug=True)