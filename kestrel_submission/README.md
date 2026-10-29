# Kestrel Motor Group — Customer Experience Data & AI Challenge

## 1. Project Overview

This project analyses customer feedback collected by Kestrel Motor Group across 24 Australian dealerships between October 2025 and September 2026.

The objective is to transform inconsistent dealership spreadsheets into a consolidated, traceable dataset, assess data quality, investigate customer feedback using NLP techniques, and identify operational improvement opportunities.

The solution focuses on three business questions:

- What are the main drivers of negative customer feedback?
- How has customer experience changed over time?
- Where should Kestrel prioritise improvements, and what might they be worth?

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Data processing and analysis |
| Pandas | Data transformation and aggregation |
| OpenPyXL | Excel file inspection |
| Scikit-learn | NLP experimentation and evaluation utilities |
| Standard Python libraries | CSV/ZIP processing, validation and rule-based text classification |
| Markdown and CSV | Reproducible reporting |

A lightweight local solution was selected to keep the workflow understandable, reproducible and inexpensive.

## 3. Data Processing

The ingestion pipeline processes 52 Excel and CSV feedback files and uses the dealership and monthly revenue reference datasets.

The canonical feedback dataset includes dealership code, feedback date, department, original rating, normalised rating, redacted comment, source lineage and quality status.

**Pipeline results:**

- Candidate records: 7,271
- Accepted records: 7,125
- Records requiring review: 146
- Rated accepted records: 7,115
- Negative ratings: 1,588
- Accepted records containing comments: 5,384

Original values and source references are preserved where possible for auditing.

## 4. Data Quality Findings

Six important source-level issues were investigated:

1. **Chermside:** Two overlapping quarterly files contained the same 112 original response IDs. The updated version added six responses and was retained.
2. **Frankston:** Twelve monthly summary rows were mixed with individual feedback and excluded from response-level analysis.
3. **Ipswich:** Ten records contained approximate or uncertain dates, which were not converted into invented exact dates.
4. **Shepparton:** Four records were outside the reporting period and after the stated closure date; an administrative note was also identified.
5. **Southport:** Four apparent test or dummy submissions were identified.
6. **Ringwood:** The Q1 workbook changed column structure and rating scale during February 2026.

All 112 accepted Ringwood Q1 responses were checked against their applicable rating normalisation formulas, with zero calculation mismatches.

Additional quality limitations remain, including subjective categorical rating mappings and potential response duplication.

Detailed decisions are recorded in `reports/data_quality_decisions.md`.

## 5. NLP and AI Approach

Customer comments were analysed using two experimental approaches.

**AI-assisted sample classification:** A sample of 120 comments received proposed sentiment, complaint-theme and actionable-complaint labels. Sixteen have completed human-review labels, although the review process included AI assistance.

**Reproducible rule-based baseline:** A transparent keyword classifier was applied to 5,384 accepted comments. It produced positive, negative, mixed and uncertain classifications, along with possible operational themes.

The baseline produced:

- Positive: 1,056
- Negative: 746
- Mixed: 118
- Uncertain: 3,464
- Flagged for further review: 4,145

On the 16 reviewed examples, exact sentiment agreement was 4/16 (25%).

These results demonstrate significant limitations, particularly with sarcasm, implicit dissatisfaction, mixed sentiment and terminology outside the predefined taxonomy.

**The rule-based classifier is not a trained LLM or validated production model.** Its results are exploratory and should not be presented as definitive customer complaint drivers.

See `reports/ai_labelling_guide.md` for methodology, evaluation findings and limitations.

## 6. Business Findings

### Department performance

| Department | Rated responses | Negative ratings | Negative rating rate |
|---|---:|---:|---:|
| Service | 4,790 | 1,284 | 26.81% |
| Parts | 689 | 111 | 16.11% |
| Sales | 1,524 | 165 | 10.83% |

Service is the strongest initial candidate for operational investigation.

Exploratory analysis suggests that communication, waiting times and pricing may be important areas to examine, subject to further NLP validation.

### Customer experience trends

The negative rating rate increased from approximately 19.8% in October 2025–March 2026 to approximately 24.6% in April–September 2026.

Changes in dealership coverage and response composition may affect this comparison.

### Priority dealership

Chermside is recommended as an initial service improvement pilot.

Its Service department recorded 87 negative ratings among 314 rated responses (27.71%), and its annual service revenue was approximately A$5.34 million.

The pilot should investigate customer communication, service delays and pricing transparency, with follow-up operational measurements.

## 7. Commercial Opportunity

A scenario model combines monthly service jobs and service revenue with the following assumptions:

- Additional service activity equivalent to 1% of historical service jobs.
- Historical average revenue per service job.
- Assumed contribution margin of 25%.

The illustrative annual contribution across open dealerships included in the model is approximately **A$193,885**.

Chermside's illustrative contribution is approximately A$13,347.

These figures are scenarios, not verified lost revenue, causal estimates or guaranteed financial benefits.

## 8. How to Run

Create and activate a Python virtual environment, then install dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Place the supplied input files under `data/raw/` using the filenames specified by the project.

Run the pipeline:

```bash
python src/pipeline.py
python src/business_analysis.py
python src/classify_feedback.py
```

Key outputs are generated in:

- `data/processed/`
- `reports/analysis/`
- `reports/run_summary.json`

Detailed findings and documentation are maintained in the `reports/` folder.

## 9. AI Usage Disclosure

AI assistance was used to accelerate data exploration, generate draft Python code, suggest classifications and help structure documentation.

The generated code was executed locally, with investigations of flagged source records and explicit validation of selected transformations.

AI-assisted customer labels were kept distinct from independently established ground truth. Evaluation limitations and disagreement examples were documented rather than hidden.

The final analysis remains subject to the limitations described in the quality and NLP reports.

## 10. Limitations and Future Improvements

- Customer feedback respondents may not represent the full customer population.
- Some rating conversions depend on documented assumptions.
- The NLP classifier has limited coverage and low preliminary agreement.
- A larger independently annotated evaluation set is needed.
- A contextual language model could improve classification but requires proper validation.
- Financial benefits are scenario-based rather than causally established.
- More robust monthly comparisons should control for dealership mix and reporting differences.

## 11. Project Reports

- `reports/data_quality_decisions.md` — source investigations and treatment decisions
- `reports/ai_labelling_guide.md` — text classification and evaluation
- `reports/business_findings.md` — business results and recommendations
- `reports/analysis/` — generated analytical CSV outputs

---

**Publicis Sapient Data & AI Challenge — Kestrel Motor Group**

This solution prioritises transparent assumptions, reproducible analysis, data quality and evidence-based business recommendations.