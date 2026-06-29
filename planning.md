# Detection Signals

## Signal 1: Sentence-Length Variation

### What it measures

The variation in sentence lengths throughout the text.

### Why it helps

Human writing usually mixes short, medium, and long sentences naturally. AI-generated text often has more consistent sentence lengths.

### Blind spot

Some humans intentionally write in a consistent style (for example, academic papers). Modern AI systems can also vary sentence lengths well, so this signal alone cannot determine authorship.

---

## Signal 2: Vocabulary Diversity

### What it measures

The ratio of unique words to the total number of words.

### Why it helps

Human writing often contains more varied vocabulary, while AI writing may repeat common words and phrases.

### Blind spot

Technical documents naturally repeat important terminology. Short pieces of writing also tend to have lower vocabulary diversity regardless of who wrote them.

---

# False Positive Scenario

Suppose a student writes an academic essay with formal language, similar sentence lengths, and repeated technical vocabulary.

The system may assign a higher AI confidence score because both detection signals appear AI-like.

Instead of claiming the writing is AI-generated, the system should return a cautious label such as **"Possibly AI-Assisted"** or **"Uncertain."**

The confidence score communicates uncertainty rather than certainty.

If the creator believes the result is incorrect, they can submit an appeal using the `POST /appeal` endpoint. Their explanation is recorded, the appeal status is updated, and the audit log keeps a record of every action for transparency.

---

# Architecture Diagram

## Submission Flow

```text
User
  |
  | Raw Text
  v
POST /submit
  |
  v
Input Validation
  |
  | Validated Text
  v
Sentence-Length Variation
  |
  | Signal Score
  v
Vocabulary Diversity
  |
  | Signal Score
  v
Confidence Scoring
  |
  | Combined Confidence Score
  v
Transparency Label Generator
  |
  | Label + Confidence
  v
Audit Log Database
  |
  | Stored Record
  v
API Response
```

---
