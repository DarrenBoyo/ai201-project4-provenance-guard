# Planning.md — Provenance Guard

## Detection Signals

### Signal 1: Sentence-Length Variation

This signal measures how much sentence lengths vary across the submitted text.

**Output:** A score from `0.0` to `1.0`.

- `0.0` = sentence lengths vary a lot, more likely human
- `1.0` = sentence lengths are very uniform, more likely AI

This works because human writing often has a natural rhythm with short, medium, and long sentences. AI writing can sometimes sound more even and predictable.

### Signal 2: Vocabulary Diversity

This signal measures how many unique words appear compared to the total number of words.

**Output:** A score from `0.0` to `1.0`.

- `0.0` = vocabulary is diverse, more likely human
- `1.0` = vocabulary is repetitive, more likely AI

This works because AI-generated writing may repeat safe or generic words. Human writing may include more personal, specific, or varied word choices.

### Combining the Signals

The system combines both signal scores using a weighted average:

```python
confidence_score = (sentence_variation_score * 0.5) + (vocabulary_diversity_score * 0.5)
```

The final `confidence_score` is also between `0.0` and `1.0`.

- Closer to `0.0` = likely human
- Closer to `1.0` = likely AI-assisted

---

## Uncertainty Representation

A confidence score represents the system's estimated AI-likelihood, not proof.

For example, a score of `0.6` means the system found some AI-like patterns, but the result is not strong enough to confidently say the text is AI-assisted. This should be treated as uncertain.

Raw signal outputs are mapped to a calibrated score by keeping each signal on a `0.0` to `1.0` scale, where higher values mean more AI-like behavior. The weighted average becomes the final confidence score.

### Thresholds

| Confidence Score | Category |
|---|---|
| `0.00 – 0.39` | Likely Human |
| `0.40 – 0.69` | Uncertain |
| `0.70 – 1.00` | Likely AI-Assisted |

These thresholds are intentionally cautious to reduce false positives.

---

## Transparency Label Design

### High-Confidence AI Result

```text
Likely AI-Assisted

This text shows several patterns commonly associated with AI-generated writing. This result is not proof of AI use, but the system has high confidence based on the available signals.
```

### High-Confidence Human Result

```text
Likely Human-Written

This text shows patterns commonly associated with human writing. This result is not proof, but the system found low evidence of AI-generated writing.
```

### Uncertain Result

```text
Uncertain

The system found mixed signals. Some patterns may look AI-assisted, while others may look human-written. This result should not be used as proof without human review.
```

---

## Appeals Workflow

A creator can submit an appeal if they believe their text was labeled incorrectly.

### Who Can Appeal?

The creator or submitter of the original text can submit an appeal.

### Appeal Request Information

The appeal must include:

- `submission_id`
- `reason`
- Optional supporting explanation from the creator

Example:

```json
{
  "submission_id": 1,
  "reason": "I wrote this myself and did not use AI assistance."
}
```

### What Happens When an Appeal Is Received?

When an appeal is received, the system:

1. Checks that the `submission_id` exists.
2. Updates the submission status to `appeal_submitted`.
3. Saves the appeal reason.
4. Adds an appeal event to the audit log.
5. Returns a confirmation response.

### What Gets Logged?

The audit log stores:

- Submission ID
- Original confidence score
- Original transparency label
- Appeal reason
- Appeal status
- Timestamp of appeal

### Human Reviewer View

A human reviewer opening the appeal queue should see:

- Submission ID
- Original submitted text
- Original signal scores
- Final confidence score
- Original label
- Creator appeal reason
- Current appeal status
- Full audit history

---

## Anticipated Edge Cases

### Edge Case 1: Academic or Technical Writing

A research paragraph or technical explanation may repeat the same key terms many times. This could lower the vocabulary diversity score and make the system think the text is more AI-like, even if it was written by a human.

### Edge Case 2: Poetry or Song-Like Writing

A poem may intentionally repeat words, phrases, or sentence structures. The system may incorrectly score it as AI-generated because repetition can look like low vocabulary diversity or uniform sentence patterns.

### Edge Case 3: Very Short Text

A short submission, such as one or two sentences, may not provide enough evidence for reliable detection. The system may return an uncertain result because both signals need enough text to be meaningful.

### Edge Case 4: Edited AI Text

If a user heavily edits AI-generated text, the writing may have more sentence variation and vocabulary diversity. The system may score it as more human-like even though AI was involved.

---

## Architecture

### Architecture Narrative

The submission flow begins when a user sends text to `POST /submit`. The system validates the text, runs two detection signals, combines the scores into a confidence score, generates a transparency label, stores the full result in the audit log, and returns the label to the user.

The appeal flow begins when a creator sends an appeal to `POST /appeal`. The system updates the submission status, records the appeal reason, adds the event to the audit log, and returns a confirmation response.

### Submission Flow Diagram

```text
User
  |
  | raw text
  v
POST /submit
  |
  | raw text
  v
Input Validator
  |
  | validated text
  v
Signal 1: Sentence-Length Variation
  |
  | sentence variation score
  v
Signal 2: Vocabulary Diversity
  |
  | vocabulary diversity score
  v
Confidence Scoring Component
  |
  | combined confidence score
  v
Transparency Label Generator
  |
  | label text + confidence score
  v
Audit Log
  |
  | saved submission, scores, label, timestamp
  v
API Response
```

### Appeal Flow Diagram

```text
Creator
  |
  | submission_id + reason
  v
POST /appeal
  |
  | appeal request
  v
Appeal Handler
  |
  | updated status
  v
Audit Log
  |
  | saved appeal event
  v
API Response
```

---

## AI Tool Plan

### M3: Submission Endpoint + First Signal

For Milestone 3, I will provide the AI tool with the **Detection Signals** section and the **Architecture** diagram.

I will ask the AI tool to generate:

- A basic Flask app skeleton
- A `POST /submit` endpoint
- Input validation for submitted text
- The first signal function: sentence-length variation
- A simple JSON response that includes the first signal score

I will verify the output by testing the signal function directly with a few inputs before connecting it fully to the endpoint.

Test examples:

- A paragraph with mixed short and long sentences
- A paragraph with very similar sentence lengths
- An empty string
- A very short text

---

### M4: Second Signal + Confidence Scoring

For Milestone 4, I will provide the AI tool with the **Detection Signals**, **Uncertainty Representation**, and **Architecture** sections.

I will ask the AI tool to generate:

- The vocabulary diversity signal function
- The weighted confidence scoring function
- Updated `/submit` logic that returns both signal scores
- Threshold logic for likely human, uncertain, and likely AI-assisted categories

I will check whether scores vary meaningfully between clearly human-style and clearly AI-style text.

I will test:

- Text with repetitive vocabulary
- Text with varied vocabulary
- Text with mixed sentence lengths
- Text with uniform sentence lengths

---

### M5: Production Layer

For Milestone 5, I will provide the AI tool with the **Transparency Label Design**, **Appeals Workflow**, and **Architecture** sections.

I will ask the AI tool to generate:

- Label generation logic
- Audit log storage
- The `POST /appeal` endpoint
- Appeal status updates
- A simple appeal queue view or response structure

I will verify that:

- All three label variants are reachable
- A high AI score returns the AI-assisted label
- A low AI score returns the human-written label
- A middle score returns the uncertain label
- An appeal changes the submission status to `appeal_submitted`
- The appeal event is recorded in the audit log
