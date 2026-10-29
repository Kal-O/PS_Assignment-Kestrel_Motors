# Data Quality Decisions

This document records key data-quality issues identified during the Kestrel Motor Group customer feedback analysis, the decisions made to address them, and the implications for reporting. Original records and source references should be retained wherever possible to support traceability.

## DQ-001: Duplicate Source Files — Chermside Q1 2026

**Issue identified:** Two versions of the Chermside Q1 2026 customer feedback file were provided.

| File | Records | Decision |
|---|---:|---|
| `Chermside Q1 2026 FINAL.xlsx` | 112 | Exclude from business analysis |
| `Chermside Q1 2026 FINAL v2.xlsx` | 118 | Retain |

### Investigation

I compared the customer response IDs across both files using Python and Pandas.

- All 112 response IDs from the original file were present in the updated file.
- The updated file contained six additional response IDs.
- No differences were found in feedback date, department, original rating, normalised rating or redacted comment for the 112 matching responses.

### Resolution

- Retain the 118 records from the updated file.
- Exclude the 112 superseded records from business analysis.
- Preserve source references and data-quality records for auditability.

### Business impact

This decision prevents duplicate customer responses from inflating feedback volumes or distorting customer experience metrics.

### Validation limitation

The comparison covered five key analytical fields. It was not a byte-for-byte comparison of the original Excel workbooks.

## DQ-002: Monthly Summary Rows — Frankston

**Issue identified:** The Frankston customer experience tracker contains monthly summary rows mixed with individual customer feedback.

### Investigation

The pipeline flagged 12 records with `invalid_date` and `unknown_department`.

I inspected the original Excel workbook and checked the source row numbers. All 12 records were confirmed to be monthly summary rows, with labels ranging from `Total Oct 2025` through `Total Sep 2026`.

These rows contain monthly average ratings rather than individual customer ratings.

### Resolution

- Exclude the 12 summary rows from response-level analysis.
- Preserve their source references in the quality audit.
- Classify them as `aggregate_summary_row` rather than treating them as genuine invalid customer dates.
- Where useful, compare the summary values with calculations from individual feedback records.

### Business impact

This avoids treating monthly averages as individual survey responses, which could distort response volumes and customer satisfaction metrics.

### Validation

All 12 flagged source rows were inspected and confirmed as monthly summary rows.

## DQ-003: Approximate Customer Feedback Dates — Ipswich

**Issue identified:** Ten customer feedback records in `IPS_feedback_log.xlsx` contain approximate or uncertain dates instead of complete calendar dates.

### Investigation

I inspected the original Excel workbook and identified values including `early Oct`, `mid Nov`, `wk1 Feb`, `wk5 Mar` and `Aug?`.

These values do not uniquely identify a calendar date.

### Resolution

- Preserve the original date values for traceability.
- Do not invent exact dates to satisfy validation rules.
- Keep records with unresolved dates flagged for review.
- Exclude records with unresolved dates from time-based analysis.
- Where the remaining information is valid, consider retaining the feedback text for thematic analysis, with an explicit record-quality indicator.

### Business impact

Assigning unsupported dates could create misleading monthly trends or suggest changes in customer satisfaction that are not supported by the original data.

### Validation

All ten QLD03 records flagged with `invalid_date` were traced to their original workbook rows and inspected.

### Limitation

Some records may be assignable to a month using contextual information, but no such inference has yet been independently verified.

## DQ-004: Dealership Closure and Out-of-Period Records — Shepparton

**Issue identified:** The Shepparton feedback workbook contains records dated after the dealership's documented closure date and outside the assignment's reporting period.

### Investigation

I compared the original workbook values against the processed dataset.

- The workbook states that Shepparton closed on 31 March 2026.
- Four feedback records are dated between 6 October and 1 December 2026.
- These records fall outside the October 2025–September 2026 reporting period.
- One additional row contains an administrative closure note rather than customer feedback.
- The pipeline flagged all five records for review.

### Resolution

- Exclude the four out-of-period records from reporting-period business analysis.
- Exclude the administrative closure note from individual customer feedback.
- Preserve the original records and their source references for audit purposes.
- Do not alter source dates without supporting evidence.

### Business impact

Including records outside the reporting period could distort monthly trends and dealership performance comparisons.

The dealership's closure must also be considered when comparing its performance with dealerships that operated throughout the reporting period.

### Limitation

The available data does not establish why feedback was recorded after Shepparton's stated closure date. These records require clarification from the source owner if they are to be used in future reporting.

## DQ-005: Test and Dummy Records — Southport

**Issue identified:** The Southport feedback tracker contains four records that appear to have been created for testing rather than genuine customer feedback.

### Investigation

I inspected the original workbook, `Southport Feedback Tracker.xlsx`, and identified the following records:

| Source row | Original date | Comment |
|---|---|---|
| 23 | 01/01/1900 | TEST TEST |
| 167 | Missing | testing new form |
| 192 | asdf | asdf |
| 196 | TEST | test - ignore |

These values strongly indicate test or dummy submissions.

### Resolution

- Exclude the four records from customer experience reporting and AI sentiment analysis.
- Preserve the original records and source row references for auditing.
- Use a descriptive validation flag such as `test_or_dummy_record`.
- Avoid permanently deleting the original records.

### Business impact

Including test submissions could distort customer satisfaction scores, negative feedback rates and automated complaint-theme results.

### Validation

All four flagged rows were inspected directly in the source workbook.

### Limitation

The records are classified as test submissions based on their contents. Their origin has not been independently confirmed by the dealership.

## DQ-006: Mid-Workbook Template Change — Ringwood

**Issue identified:** The Ringwood Q1 2026 feedback workbook changes its template partway through the reporting period.

### Investigation

I inspected the original workbook and identified the following:

- Row 36 contains `*** NEW TEMPLATE FROM FEB 2026 ***`.
- Row 37 contains new column headings.
- Rows before the marker use the original feedback structure.
- Rows after the marker use a revised structure.

### Resolution

- Exclude the template-change marker and repeated header row from customer feedback.
- Preserve source row references in the quality audit.
- Treat the original and revised sections as separate input layouts.
- Validate column mappings and rating scales independently for each section.

### Business impact

Reading the entire workbook using one column mapping could misinterpret customer ratings, dates or other attributes. This could distort dealership satisfaction scores and monthly trends.

### Validation limitation

The template-change marker has been verified, but the full mapping and rating-scale handling of the revised section still require validation. Until this validation is complete, results dependent on the revised section should be interpreted cautiously.