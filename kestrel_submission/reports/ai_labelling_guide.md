# Customer Feedback AI Labelling Guide

## Purpose

To classify dealership customer comments consistently and evaluate the accuracy of AI-generated labels.

## 1. Sentiment labels

- **positive:** The comment expresses satisfaction without a meaningful complaint.
- **negative:** The comment primarily expresses dissatisfaction.
- **mixed:** The comment contains both meaningful praise and criticism.
- **neutral:** The comment is factual or does not express clear satisfaction or dissatisfaction.

Sentiment must be determined from the text, not automatically from the numerical rating.

## 2. Complaint and feedback themes

Multiple themes may apply to one comment.

| Theme | Definition |
|---|---|
| Communication | Customer updates, callbacks, explanations and information sharing |
| Waiting & delays | Waiting times, late completion and delivery delays |
| Price & billing | Unexpected charges, pricing disputes and unclear quotes |
| Parts availability | Parts shortages, backorders and sourcing delays |
| Quality & repairs | Repair effectiveness, workmanship, unresolved faults and repeat repairs |
| Staff & courtesy | Staff attitude, helpfulness, politeness and professionalism |

Only assign a theme when the text provides evidence. Theme presence does not automatically indicate negative sentiment.

## 3. Actionable complaint

- **yes:** The comment describes a specific problem that the dealership could reasonably investigate or improve.
- **no:** The comment contains no identifiable actionable problem.

A mixed-sentiment comment may still contain an actionable complaint.

## 4. Human annotation rules

1. Read the entire comment before assigning labels.
2. Do not use the customer rating to determine sentiment.
3. Assign multiple themes where justified.
4. Avoid inferring problems that are not explicitly supported by the text.
5. Record ambiguous cases for review.
6. Preserve the original redacted comments.
7. Do not treat automated keyword matches as verified ground truth.

## 5. Evaluation

Compare AI predictions against the independently reviewed human-labelled sample.

Report sentiment classification accuracy and a confusion matrix.

For multi-label themes, calculate precision, recall and F1 scores.

Inspect disagreement examples and describe model limitations.

The evaluation sample is balanced by rating group and must not be treated as representative of the overall customer sentiment distribution.

## Preliminary AI Evaluation Results

A sample of 120 customer comments was selected for AI classification and human review.

At the current evaluation checkpoint, 16 comments had completed human labels.

### Results

- Sentiment classification agreement: 16/16 (100%).
- Actionable complaint agreement: 16/16 (100%).
- Sentiment breakdown: 12 negative, 3 mixed and 1 positive.
- No disagreements were found in the reviewed subset.

### Limitations

These results should not be interpreted as an unbiased estimate of model accuracy.

The reviewed subset is small, heavily weighted towards negative feedback and contains AI-assisted human labels. The human labels were not produced through a fully independent blinded annotation process.

The remaining 104 sampled comments have not yet been independently verified.

### Next validation steps

Conduct an independent, blinded review of additional comments, including positive, negative, mixed and ambiguous cases.

Calculate sentiment accuracy and multi-label theme precision, recall and F1 scores against the independently reviewed labels.

Investigate disagreements and document limitations in the complaint-theme taxonomy.

## Rule-Based NLP Baseline Evaluation

A transparent keyword-based NLP classifier was applied to 5,384 accepted customer comments.

### Classification results

- Positive: 1,056
- Negative: 746
- Mixed: 118
- Uncertain: 3,464
- Flagged for review: 4,145

### Preliminary evaluation

The classifier was compared with 16 reviewed customer comments.

- Exact sentiment agreement: 4/16 (25%).
- Disagreements or uncertain classifications: 12/16.
- The evaluation sample is small and contains AI-assisted reference labels.

### Observed limitations

The baseline struggled with implied dissatisfaction, sarcasm, mixed sentiment and complaints involving topics outside the original six categories.

For example, the comment "Quoted two hours, took six" was classified as uncertain despite clearly describing an excessive delay.

### Interpretation

Keyword matching provides a transparent and reproducible baseline, but these results demonstrate that it is insufficient for reliable sentiment classification without further validation and improvement.

The keyword-derived theme counts are therefore exploratory and should not be treated as independently established complaint drivers.

### Recommended improvement

A context-aware language model with structured multi-label output could improve coverage of complex customer feedback.

Any proposed model should be evaluated using independently annotated comments before its classifications are used for operational decisions.
