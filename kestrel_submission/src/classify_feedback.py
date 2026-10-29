
from pathlib import Path
import re
import pandas as pd

# Resolve paths relative to the project, not the terminal's directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT = PROJECT_ROOT / "data" / "processed" / "feedback_clean.csv"
OUTPUT = PROJECT_ROOT / "data" / "processed" / "feedback_nlp.csv"

# Operational themes. A comment can match multiple themes.
THEMES = {
    "Communication": [
        r"\bcall(?:ed|ing|s)?\b",
        r"\btext(?:ed|ing|s)?\b",
        r"\bupdates?\b",
        r"\bexplain(?:ed|ing|s)?\b",
        r"\bmessages?\b",
        r"\bcontact(?:ed|ing)?\b",
        r"\bcommunicat\w*\b",
        r"\bemail(?:ed|s)?\b",
        r"\bphone(?:d|s)?\b",
        r"\bno response\b",
        r"\bno reply\b",
        r"\bkept me informed\b",
    ],
    "Waiting & delays": [
        r"\bwait(?:ed|ing|s)?\b",
        r"\bslow(?:ly)?\b",
        r"\blate\b",
        r"\bdelay(?:ed|s)?\b",
        r"\bhours?\b",
        r"\bappointment\b",
        r"\btime(?:ly)?\b",
        r"\btoo long\b",
        r"\bwaiting for\b",
        r"\bon time\b",
        r"\bready when\b",
    ],
    "Price & billing": [
        r"\bcharg(?:e|ed|ing|es)\b",
        r"\bbill(?:ed|ing|s)?\b",
        r"\bprice(?:s|y)?\b",
        r"\bquotes?\b",
        r"\binvoices?\b",
        r"\bcost(?:s|ly)?\b",
        r"\bexpensive\b",
        r"\brefund(?:ed|s)?\b",
        r"\bovercharg\w*\b",
        r"\bpayment\b",
        r"\bdiscount\b",
        r"\bunexpected charge\b",
    ],
    "Parts availability": [
        r"\bback.?order\w*\b",
        r"\bout of stock\b",
        r"\bparts?\b",
        r"\bspare parts?\b",
        r"\bunavailable\b",
        r"\bmissing parts?\b",
        r"\bparts? (?:late|missing|unavailable)\b",
        r"\bparts? (?:arriv|order)\w*\b",
        r"\bwaiting for (?:a )?part\w*\b",
    ],
    "Quality & repairs": [
        r"\brepair(?:ed|ing|s)?\b",
        r"\bservic(?:e|ed|ing)\b",
        r"\bstill broken\b",
        r"\bnot fixed\b",
        r"\bscratch(?:ed|es)?\b",
        r"\bfault(?:y|s)?\b",
        r"\bproblem(?:s)?\b",
        r"\bissue(?:s)?\b",
        r"\bdefect(?:ive|s)?\b",
        r"\brattl(?:e|ed|ing|es)\b",
        r"\bvibrat\w*\b",
        r"\bengine\b",
        r"\bwarning light\b",
        r"\bwrong repair\b",
    ],
    "Staff & courtesy": [
        r"\bstaff\b",
        r"\bservice advisor\b",
        r"\bmanager\b",
        r"\brude\b",
        r"\bdismissive\b",
        r"\bhelpful\b",
        r"\bfriendly\b",
        r"\bpolite\b",
        r"\bcondescending\b",
        r"\bprofessional\b",
        r"\bcourteous\b",
        r"\bunhelpful\b",
        r"\battitude\b",
        r"\btreated me\b",
    ],
}

# Common negative expressions.
NEGATIVE_PATTERNS = [
    r"\bnever\b",
    r"\bno (?:call|update|reply|response|communication)\b",
    r"\bpoor\b",
    r"\bterrible\b",
    r"\brubbish\b",
    r"\bnot happy\b",
    r"\bnot satisfied\b",
    r"\bunsatisfied\b",
    r"\bdissatisfied\b",
    r"\bawful\b",
    r"\bexcessive\b",
    r"\bdodgy\b",
    r"\bwasn't\b",
    r"\bweren't\b",
    r"\bdidn't\b",
    r"\bdoesn't\b",
    r"\bdon't\b",
    r"\bcouldn't\b",
    r"\bwouldn't\b",
    r"\bshouldn't\b",
    r"\btoo long\b",
    r"\bstill waiting\b",
    r"\bdisappoint\w*\b",
    r"\bfrustrat\w*\b",
    r"\bunacceptable\b",
    r"\bincorrect\b",
    r"\bwrong\b",
    r"\bunhelpful\b",
    r"\bunprofessional\b",
    r"\bfailed\b",
    r"\bcharged too much\b",
    r"\bnot fixed\b",
    r"\bno one\b",
    r"\bnever again\b",
]

# Common positive expressions.
POSITIVE_PATTERNS = [
    r"\bexcellent\b",
    r"\bgreat\b",
    r"\bfantastic\b",
    r"\bhelpful\b",
    r"\bfriendly\b",
    r"\bthank(?:s| you)?\b",
    r"\bbrilliant\b",
    r"\bquick(?:ly)?\b",
    r"\bsmooth(?:ly)?\b",
    r"\bappreciat\w*\b",
    r"\bprofessional\b",
    r"\bexcellent service\b",
    r"\bwell done\b",
    r"\bvery happy\b",
    r"\bhighly recommend\w*\b",
    r"\bpleasant\b",
    r"\befficient\b",
    r"\bprompt\b",
    r"\bsatisfied\b",
    r"\bno problems?\b",
    r"\beasy process\b",
    r"\bkept me informed\b",
    r"\bwent above and beyond\b",
    r"\blooked after me\b",
]

# Expressions that more directly suggest an actionable complaint.
COMPLAINT_PATTERNS = [
    r"\bcomplain\w*\b",
    r"\bnot fixed\b",
    r"\bwrong\b",
    r"\bmissing\b",
    r"\bno (?:call|update|reply|response)\b",
    r"\bovercharg\w*\b",
    r"\bcharged too much\b",
    r"\bunacceptable\b",
    r"\bunresolved\b",
    r"\bdisappoint\w*\b",
    r"\bpoor service\b",
    r"\bdamage(?:d)?\b",
    r"\brefund\b",
    r"\bunsafe\b",
    r"\bnever again\b",
]


def matches(text, patterns):
    """Return True if any supplied regular expression matches."""
    return any(re.search(pattern, text, re.IGNORECASE)
               for pattern in patterns)


def classify(text):
    """Apply transparent keyword rules to one customer comment."""

    # Avoid treating missing values as the literal text 'nan'.
    if pd.isna(text):
        text = ""
    else:
        text = str(text).strip()

    if not text:
        return pd.Series({
            "nlp_sentiment": "uncertain",
            "nlp_themes": "",
            "nlp_actionable_complaint": "uncertain",
            "nlp_needs_review": True,
            "nlp_sentiment_needs_review": True,
            "nlp_theme_needs_review": True,
        })

    themes = [
        theme
        for theme, patterns in THEMES.items()
        if matches(text, patterns)
    ]

    has_negative = matches(text, NEGATIVE_PATTERNS)
    has_positive = matches(text, POSITIVE_PATTERNS)

    if has_negative and has_positive:
        sentiment = "mixed"
    elif has_negative:
        sentiment = "negative"
    elif has_positive:
        sentiment = "positive"
    else:
        sentiment = "uncertain"

    # This is a rule-based indicator, not a confirmed complaint label.
    if matches(text, COMPLAINT_PATTERNS):
        complaint = "possible"
    elif sentiment == "negative":
        complaint = "possible"
    else:
        complaint = "uncertain"

    sentiment_needs_review = sentiment == "uncertain"
    theme_needs_review = len(themes) == 0

    return pd.Series({
        "nlp_sentiment": sentiment,
        "nlp_themes": "|".join(themes),
        "nlp_actionable_complaint": complaint,
        "nlp_needs_review": (
            sentiment_needs_review or theme_needs_review
        ),
        "nlp_sentiment_needs_review": sentiment_needs_review,
        "nlp_theme_needs_review": theme_needs_review,
    })


def main():
    if not INPUT.is_file():
        raise FileNotFoundError(
            f"Input file not found: {INPUT}\n"
            "Run the data-processing pipeline first and check the path."
        )

    df = pd.read_csv(INPUT)

    required_columns = {
        "qa_status",
        "comment_redacted",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        raise ValueError(
            f"Input file is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    comments = df[
        (df["qa_status"] == "accepted")
        & df["comment_redacted"].notna()
        & df["comment_redacted"].astype(str).str.strip().ne("")
    ].copy()

    predictions = comments["comment_redacted"].apply(classify)

    # Avoid duplicating the index and preserve the original comment columns.
    result = pd.concat(
        [
            comments.reset_index(drop=True),
            predictions.reset_index(drop=True),
        ],
        axis=1,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    print("Comments classified:", len(result))

    print("\nSentiment distribution:")
    print(result["nlp_sentiment"].value_counts())

    print("\nSentiment review required:")
    print(result["nlp_sentiment_needs_review"].sum())

    print("\nTheme review required:")
    print(result["nlp_theme_needs_review"].sum())

    print("\nOverall review required:")
    print(result["nlp_needs_review"].sum())

    print("\nPotential complaints:")
    print(
        (result["nlp_actionable_complaint"] == "possible").sum()
    )

    print("\nOutput:", OUTPUT)


if __name__ == "__main__":
    main()

