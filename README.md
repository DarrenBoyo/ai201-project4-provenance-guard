# Provenance Guard

Provenance Guard is a Flask-based API that analyzes submitted text and returns a transparency label indicating whether the text appears **Likely Human-Written**, **Uncertain**, or **Likely AI-Assisted**. The system uses two detection signals, combines them into a confidence score, logs every classification decision, supports creator appeals, and applies rate limiting to prevent abuse.

---

# Architecture Overview

A submission begins when a user sends a JSON request containing a piece of text and a creator ID to the `POST /submit` endpoint. The API validates the request, generates a unique `content_id`, computes two detection signals, combines them into a confidence score, generates a transparency label, stores the result in the audit log, and returns the classification to the user.

If a creator believes the classification is incorrect, they can submit an appeal using the `POST /appeal` endpoint. The system records the appeal, updates the submission status to **under review**, logs the appeal, and returns a confirmation message.

## Submission Flow

```text
User
  |
  | text + creator_id
  v
POST /submit
  |
  v
Input Validation
  |
  v
Signal 1:
Sentence-Length Variation
  |
  v
Signal 2:
AI Marker / Formal Language Density
  |
  v
Confidence Scoring
  |
  v
Transparency Label
  |
  v
Audit Log
  |
  v
JSON Response
```

## Appeal Flow

```text
Creator
  |
  | content_id + creator_reasoning
  v
POST /appeal
  |
  v
Update Status
  |
  v
Audit Log
  |
  v
JSON Response
```

---

# Detection Signals

## Signal 1: Sentence-Length Variation

### What it measures

This signal measures how much sentence lengths vary throughout the submitted text.

### Why I chose it

Human writing usually contains a natural mixture of short, medium, and long sentences. AI-generated writing can sometimes be more uniform and consistent.

### Limitations

Academic writing, legal writing, and technical documentation often contain very consistent sentence structures. These can appear AI-like even when written entirely by a person.

---

## Signal 2: AI Marker / Formal Language Density

### What it measures

This signal searches for common AI-style phrases and highly formal language, including expressions such as:

- "It is important to note"
- "Furthermore"
- "Transformative"
- "Paradigm shift"
- "Stakeholders"
- "Ethical implications"

### Why I chose it

I originally planned to use vocabulary diversity as my second signal. During testing, however, vocabulary diversity produced nearly identical scores across many different writing samples, making it ineffective.

I replaced it with AI marker detection because it produced much more meaningful differences between the required test inputs.

### Limitations

This signal may incorrectly classify formal academic or business writing because those writing styles naturally use formal language and transition phrases.

Likewise, heavily edited AI-generated writing may avoid these phrases and therefore receive a lower AI score.

---

## Confidence Scoring

Each detection signal produces a score between **0.0** and **1.0**, where larger values indicate stronger AI-like characteristics.

The final confidence score is calculated using a weighted average:

```python
confidence = (sentence_score * 0.3) + (vocabulary_score * 0.7)
```

The second detection signal receives a larger weight because testing showed that the AI marker and formal-language detector distinguished AI-generated text from human-written text more effectively than sentence-length variation alone. The sentence-length signal still contributes to the overall score by measuring writing rhythm and structural consistency.

The confidence score is mapped to three transparency categories:

| Confidence Score | Classification       |
| ---------------- | -------------------- |
| 0.00 – 0.39      | Likely Human-Written |
| 0.40 – 0.69      | Uncertain            |
| 0.70 – 1.00      | Likely AI-Assisted   |

### Validation

To ensure the scoring system produced meaningful variation, I tested the detector using four different writing samples: a clearly AI-generated paragraph, a clearly human-written paragraph, formal academic writing, and lightly edited AI text.

Two representative examples are shown below.

### Example 1 — High Confidence AI

**Input (excerpt)**

> "Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous..."

**Output**

```json
{
  "confidence": 0.79,
  "attribution": "likely_ai",
  "sentence_variation_score": 0.41,
  "vocabulary_diversity_score": 0.96
}
```

The confidence score is high because the submission contains several formal AI-style phrases, including *"It is important to note," "transformative paradigm shift," "ethical implications,"* and *"stakeholders."* These phrases strongly influenced the second detection signal.

---

### Example 2 — Low Confidence Human

**Input (excerpt)**

> "ok so i finally tried that new ramen place downtown and honestly? underwhelming..."

**Output**

```json
{
  "confidence": 0.03,
  "attribution": "likely_human",
  "sentence_variation_score": 0.10,
  "vocabulary_diversity_score": 0.00
}
```

This submission received a much lower confidence score because it is conversational, informal, and does not contain the formal language patterns targeted by the second detection signal.

These examples demonstrate that the confidence scoring system produces meaningful variation instead of assigning nearly identical confidence values to every submission.

---

# Transparency Labels

The transparency label returned by the API changes based on the final confidence score.

## High-Confidence AI

Displayed when the confidence score is **0.70 or higher**.

```text
Likely AI-Assisted

This text shows several patterns commonly associated with AI-generated writing. This result is not proof of AI use, but the system has high confidence based on the available signals.
```

---

## High-Confidence Human

Displayed when the confidence score is **0.39 or lower**.

```text
Likely Human-Written

This text shows patterns commonly associated with human writing. This result is not proof, but the system found low evidence of AI-generated writing.
```

---

## Uncertain

Displayed when the confidence score falls between **0.40 and 0.69**.

```text
Uncertain

The system found mixed signals. Some patterns may look AI-assisted, while others may look human-written. This result should not be used as proof without human review.
```

---

# Known Limitations

The current system relies on lightweight heuristic signals rather than a trained machine learning model, so there are situations where it may misclassify content.

One example is **formal academic or technical writing**. Research papers, policy reports, and business documents often contain transition phrases and formal vocabulary such as *"furthermore," "stakeholders,"* and *"fundamental."* Because the second detection signal searches for these patterns, the system may incorrectly assign a higher AI confidence score to writing that was created entirely by a human.

Another limitation is **AI-generated text that has been heavily edited**. If a user rewrites AI-generated text to remove obvious AI phrases and introduces more natural sentence variation, the heuristic signals may incorrectly classify the submission as human-written even though AI was used during drafting.

If this project were deployed in a production environment, I would replace the heuristic detector with a trained machine learning model, evaluate it using a larger and more diverse validation dataset, and calibrate the confidence thresholds using empirical performance data.

---

# Spec Reflection

## One way the specification helped

The milestone-based structure encouraged incremental development. Building the submission endpoint first, then implementing one detection signal before adding confidence scoring and production features, made it much easier to isolate bugs and verify each component before moving to the next milestone.

## One way the implementation diverged

My original design planned to use vocabulary diversity as the second detection signal. During testing, vocabulary diversity produced nearly identical values for many different writing samples, making it ineffective for distinguishing AI-generated text from human-written text. I replaced that signal with an AI marker and formal-language detector because it produced more meaningful confidence scores while still satisfying the requirement to combine multiple detection signals.

---

# AI Usage

## Instance 1 — Flask Application

I directed the AI assistant to generate the initial Flask application, including the API structure, the `/submit` endpoint, request validation, JSON responses, and helper functions for reading and writing the audit log.

The generated code provided a solid starting point, but I revised it to generate unique `content_id` values, match the API contract defined in my planning document, and ensure that every submission produced a structured audit log entry.

---

## Instance 2 — Detection Signals and Confidence Scoring

I asked the AI assistant to generate the second detection signal and the confidence-scoring logic using the architecture diagram and planning document.

The first implementation used vocabulary diversity as the second signal. After testing with the required examples, I discovered that vocabulary diversity produced nearly identical scores for most submissions. I replaced it with an AI marker and formal-language detector and adjusted the confidence weighting from an equal average to a weighted average so that the scoring better matched the expected behavior of the required test cases.

---

## Instance 3 — Production Features

I used the AI assistant to help implement the transparency label generator, the `/appeal` endpoint, and Flask-Limiter integration.

After reviewing the generated code, I manually tested every feature using `curl` commands. I verified that:

* the correct transparency label was returned for each confidence range,
* submitting an appeal created an audit log entry with `"status": "under_review"`,
* and exceeding the configured submission limit resulted in **HTTP 429 (Too Many Requests)** responses, confirming that rate limiting was functioning correctly.
---

# Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
python app.py
```

Submit text:

```bash
curl -X POST http://localhost:5000/submit \
-H "Content-Type: application/json" \
-d "{\"text\":\"Example text\",\"creator_id\":\"user1\"}"
```

View the audit log:

```bash
curl http://localhost:5000/log
```

Submit an appeal:

```bash
curl -X POST http://localhost:5000/appeal \
-H "Content-Type: application/json" \
-d "{\"content_id\":\"YOUR_CONTENT_ID\",\"creator_reasoning\":\"I wrote this myself.\"}"
```
