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

# Confidence Scoring

Both signals produce values between **0.0** and **1.0**, where larger values indicate more AI-like characteristics.

The final confidence score is calculated using a weighted average:

```python
confidence = (sentence_score * 0.3) + (vocabulary_score * 0.7)
```

The second signal receives a larger weight because testing showed it separated AI-like writing from casual human writing more effectively than sentence-length variation.

The final score maps to three confidence ranges:

| Confidence | Result |
|------------|--------|
| 0.00 – 0.39 | Likely Human |
| 0.40 – 0.69 | Uncertain |
| 0.70 – 1.00 | Likely AI-Assisted |

## Validation

I tested the scoring using four different writing samples:

- Clearly AI-generated
- Clearly human-written
- Formal human writing
- Lightly edited AI writing

The AI sample received a substantially higher score than the human sample.

### Example: High Confidence AI

```json
{
    "confidence": 0.79,
    "attribution": "likely_ai",
    "sentence_variation_score": 0.41,
    "vocabulary_diversity_score": 0.96
}
```

### Example: Low Confidence Human

```json
{
    "confidence": 0.03,
    "attribution": "likely_human",
    "sentence_variation_score": 0.10,
    "vocabulary_diversity_score": 0.00
}
```

---

# Transparency Labels

The API displays one of three transparency labels.

## Likely AI-Assisted

```text
Likely AI-Assisted

This text shows several patterns commonly associated with AI-generated writing. This result is not proof of AI use, but the system has high confidence based on the available signals.
```

---

## Likely Human-Written

```text
Likely Human-Written

This text shows patterns commonly associated with human writing. This result is not proof, but the system found low evidence of AI-generated writing.
```

---

## Uncertain

```text
Uncertain

The system found mixed signals. Some patterns may look AI-assisted, while others may look human-written. This result should not be used as proof without human review.
```

---

# Appeals Workflow

Creators can challenge a classification using the `/appeal` endpoint.

The request contains:

```json
{
    "content_id": "...",
    "creator_reasoning": "I wrote this myself."
}
```

When an appeal is submitted the system:

1. Records the appeal.
2. Updates the submission status to **under_review**.
3. Adds an appeal event to the audit log.
4. Returns a confirmation response.

The audit log stores:

- content ID
- timestamp
- appeal status
- creator reasoning
- event type

---

# Rate Limiting

The `/submit` endpoint uses Flask-Limiter with the following limits:

```python
@limiter.limit("10 per minute;100 per day")
```

### Why these limits?

A normal user submitting their own work is unlikely to submit more than ten pieces of writing within one minute.

The daily limit of one hundred submissions still allows frequent testing while preventing automated abuse or denial-of-service attacks.

During testing, requests beyond the limit correctly returned **HTTP 429 (Too Many Requests).**

---

# Audit Log

Every submission creates a structured JSON log entry.

Each entry contains:

- Timestamp
- Content ID
- Creator ID
- Attribution
- Confidence score
- Sentence variation score
- AI marker score
- Transparency label
- Appeal status
- Event type

Appeals generate additional log entries with:

- Status = `under_review`
- Appeal reasoning
- Event type = `appeal_submitted`

The `/log` endpoint returns the most recent audit log entries as JSON.

---

# Known Limitations

One limitation is **formal academic writing**.

Research papers and technical reports often use phrases similar to AI-generated writing, causing the AI marker signal to produce higher confidence scores even when the text is entirely human-written.

Another limitation is **edited AI output**.

If AI-generated text is rewritten to remove obvious AI phrases and make sentence lengths more varied, the system may incorrectly classify it as human-written.

In a production environment, I would replace these simple heuristics with a trained machine learning model evaluated on a much larger and more diverse dataset.

---

# Spec Reflection

## How the specification helped

The milestone-based specification encouraged building one feature at a time. Developing the first detection signal before adding the second made debugging much easier because each component could be tested independently.

## Where implementation diverged

The original plan called for vocabulary diversity as the second signal. During testing, vocabulary diversity produced very similar scores for nearly every input, making it ineffective. I replaced it with an AI marker and formal-language signal because it better separated the required AI and human test cases.

---

# AI Usage

## Instance 1

I used AI to generate the initial Flask application, including the API structure, `/submit` endpoint, input validation, JSON responses, and audit logging.

I reviewed and modified the generated code to match my planned API specification and ensured every response included the required fields.

## Instance 2

I used AI to help generate the second detection signal and confidence-scoring logic.

The initial vocabulary-diversity approach did not distinguish between the required test inputs, so I replaced it with an AI marker detection approach and adjusted the signal weights after testing multiple examples until the confidence scores better matched the expected outcomes.

## Instance 3

I used AI to help implement the `/appeal` endpoint, transparency label generation, and Flask-Limiter configuration. I manually tested each feature using `curl` commands to verify that appeals were logged correctly and that rate limiting returned HTTP 429 responses after the request limit was exceeded.

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
