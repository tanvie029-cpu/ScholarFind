from flask import Flask, render_template, request
import pandas as pd
import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "scholarships.csv")


# =========================================================
# LOAD DATASET
# =========================================================

df = pd.read_csv(DATASET_PATH).fillna("")


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_column_name(name):
    """
    Cleans CSV column names.

    Example:
        **state
        income_limit
        Scholarship Name

    become easier to detect.
    """
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(name).lower()
    ).strip()


def find_column(possible_names):
    """
    Finds a dataset column even if the CSV contains
    slightly different formatting.
    """

    columns = {
        column: clean_column_name(column)
        for column in df.columns
    }

    for wanted in possible_names:

        wanted_clean = clean_column_name(wanted)

        for column, cleaned in columns.items():

            if (
                cleaned == wanted_clean
                or wanted_clean in cleaned
            ):
                return column

    return None


def clean_url(value):
    """
    Converts both normal URLs and Markdown-style URLs
    into a valid browser URL.

    Example:

    [https://scholarships.gov.in/](https://scholarships.gov.in/)

    becomes:

    https://scholarships.gov.in/
    """

    value = str(value).strip()

    if not value:
        return ""

    markdown_match = re.search(
        r"\]\((https?://[^)\s]+)\)",
        value
    )

    if markdown_match:
        return markdown_match.group(1)

    url_match = re.search(
        r"https?://[^\s)]+",
        value
    )

    if url_match:
        return url_match.group(0)

    return ""


def display_value(value, fallback="Not specified"):

    value = str(value).strip()

    if value:
        return value

    return fallback


# =========================================================
# FIND DATASET COLUMNS
# =========================================================

NAME_COLUMN = find_column([
    "scholarship_name",
    "scholarship name",
    "scholarship",
    "name",
    "title"
])

DESCRIPTION_COLUMN = find_column([
    "description",
    "details",
    "about",
    "summary"
])

PROVIDER_COLUMN = find_column([
    "provider",
    "organization",
    "organisation",
    "institution",
    "sponsor"
])

ELIGIBILITY_COLUMN = find_column([
    "eligibility",
    "eligible",
    "criteria",
    "requirements"
])

AMOUNT_COLUMN = find_column([
    "amount",
    "award",
    "prize",
    "benefit",
    "value"
])

COURSE_COLUMN = find_column([
    "course"
])

LEVEL_COLUMN = find_column([
    "level"
])

CATEGORY_COLUMN = find_column([
    "category",
    "caste"
])

GENDER_COLUMN = find_column([
    "gender",
    "sex"
])

STATE_COLUMN = find_column([
    "state",
    "region",
    "location"
])

INCOME_COLUMN = find_column([
    "income_limit",
    "income limit",
    "income"
])

PERCENTAGE_COLUMN = find_column([
    "minimum_percentage",
    "minimum percentage",
    "percentage",
    "marks",
    "minimum"
])

DEADLINE_COLUMN = find_column([
    "deadline",
    "last date",
    "closing date"
])

URL_COLUMN = find_column([
    "application_url",
    "application url",
    "url",
    "link"
])


# =========================================================
# SEARCH DATA
# =========================================================

search_columns = [
    column
    for column in df.select_dtypes(include="object").columns
    if column != URL_COLUMN
]

if search_columns:

    df["search_text"] = (
        df[search_columns]
        .astype(str)
        .agg(" ".join, axis=1)
    )

else:

    df["search_text"] = ""


# =========================================================
# TF-IDF
# =========================================================

vectorizer = TfidfVectorizer(
    stop_words="english",
    lowercase=True,
    ngram_range=(1, 2)
)

tfidf_matrix = vectorizer.fit_transform(
    df["search_text"]
)


# =========================================================
# TEXT PROCESSING
# =========================================================

def preprocess_text(text):

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def keyword_score(query, document):

    query_words = set(
        preprocess_text(query).split()
    )

    document_words = set(
        preprocess_text(document).split()
    )

    if not query_words:
        return 0.0

    common_words = (
        query_words &
        document_words
    )

    return len(common_words) / len(query_words)


def title_score(query, title):

    query_words = set(
        preprocess_text(query).split()
    )

    title_words = set(
        preprocess_text(title).split()
    )

    if not query_words:
        return 0.0

    common_words = (
        query_words &
        title_words
    )

    return len(common_words) / len(query_words)


# =========================================================
# FILTER OPTIONS
# =========================================================

def get_filter_values(column):

    if not column:
        return []

    values = (
        df[column]
        .astype(str)
        .str.strip()
    )

    values = values[
        values != ""
    ].unique().tolist()

    return sorted(
        values,
        key=str.lower
    )


course_values = get_filter_values(
    COURSE_COLUMN
)

category_values = get_filter_values(
    CATEGORY_COLUMN
)

gender_values = get_filter_values(
    GENDER_COLUMN
)

state_values = get_filter_values(
    STATE_COLUMN
)


# =========================================================
# FILTERING
# =========================================================

def contains_value(series, value):

    return series.astype(str).str.contains(
        re.escape(str(value)),
        case=False,
        na=False
    )


def apply_filters(
    data,
    course,
    category,
    gender,
    state,
    max_income,
    min_percentage
):

    filtered = data.copy()

    # -----------------------------------------------------
    # COURSE
    # -----------------------------------------------------

    if course and COURSE_COLUMN:

        filtered = filtered[
            contains_value(
                filtered[COURSE_COLUMN],
                course
            )
        ]


    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    if category and CATEGORY_COLUMN:

        category_match = contains_value(
            filtered[CATEGORY_COLUMN],
            category
        )

        all_match = contains_value(
            filtered[CATEGORY_COLUMN],
            "all"
        )

        filtered = filtered[
            category_match | all_match
        ]


    # -----------------------------------------------------
    # GENDER
    # -----------------------------------------------------

    if gender and GENDER_COLUMN:

        gender_match = contains_value(
            filtered[GENDER_COLUMN],
            gender
        )

        all_match = contains_value(
            filtered[GENDER_COLUMN],
            "all"
        )

        filtered = filtered[
            gender_match | all_match
        ]


    # -----------------------------------------------------
    # STATE
    # -----------------------------------------------------

    if state and STATE_COLUMN:

        state_match = contains_value(
            filtered[STATE_COLUMN],
            state
        )

        all_match = contains_value(
            filtered[STATE_COLUMN],
            "all"
        )

        filtered = filtered[
            state_match | all_match
        ]


    # -----------------------------------------------------
    # MAXIMUM INCOME
    # -----------------------------------------------------

    if max_income and INCOME_COLUMN:

        try:
            maximum_income = float(
                max_income
            )

        except ValueError:
            maximum_income = None

        if maximum_income is not None:

            def income_allowed(value):

                numbers = re.findall(
                    r"\d+(?:\.\d+)?",
                    str(value).replace(",", "")
                )

                if not numbers:
                    return True

                return (
                    float(numbers[0])
                    <= maximum_income
                )

            filtered = filtered[
                filtered[INCOME_COLUMN]
                .apply(income_allowed)
            ]


    # -----------------------------------------------------
    # MINIMUM PERCENTAGE
    # -----------------------------------------------------

    if min_percentage and PERCENTAGE_COLUMN:

        try:
            minimum_percentage = float(
                min_percentage
            )

        except ValueError:
            minimum_percentage = None

        if minimum_percentage is not None:

            def percentage_allowed(value):

                numbers = re.findall(
                    r"\d+(?:\.\d+)?",
                    str(value)
                )

                if not numbers:
                    return True

                return (
                    float(numbers[0])
                    >= minimum_percentage
                )

            filtered = filtered[
                filtered[PERCENTAGE_COLUMN]
                .apply(percentage_allowed)
            ]


    return filtered


# =========================================================
# SCHOLARSHIP SEARCH + RANKING
# =========================================================

def search_scholarships(
    query,
    filtered_df
):

    if filtered_df.empty:
        return filtered_df

    query_vector = vectorizer.transform(
        [query]
    )

    indexes = filtered_df.index.tolist()

    filtered_matrix = tfidf_matrix[
        indexes
    ]

    cosine_scores = cosine_similarity(
        query_vector,
        filtered_matrix
    ).flatten()

    results_df = filtered_df.copy()

    results_df["tfidf_score"] = (
        cosine_scores
    )

    results_df["keyword_score"] = (
        results_df["search_text"]
        .apply(
            lambda text:
            keyword_score(
                query,
                text
            )
        )
    )

    if NAME_COLUMN:

        results_df["title_score"] = (
            results_df[NAME_COLUMN]
            .apply(
                lambda title:
                title_score(
                    query,
                    title
                )
            )
        )

    else:

        results_df["title_score"] = 0.0


    # Final relevance score
    results_df["final_score"] = (
        0.70 *
        results_df["tfidf_score"]
        +
        0.20 *
        results_df["keyword_score"]
        +
        0.10 *
        results_df["title_score"]
    )

    return (
        results_df
        .sort_values(
            by="final_score",
            ascending=False
        )
        .head(10)
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    results = []

    query = ""

    selected_course = ""
    selected_category = ""
    selected_gender = ""
    selected_state = ""
    selected_income = ""
    selected_percentage = ""

    searched = request.method == "POST"


    if searched:

        query = request.form.get(
            "query",
            ""
        ).strip()

        selected_course = request.form.get(
            "course",
            ""
        ).strip()

        selected_category = request.form.get(
            "category",
            ""
        ).strip()

        selected_gender = request.form.get(
            "gender",
            ""
        ).strip()

        selected_state = request.form.get(
            "state",
            ""
        ).strip()

        selected_income = request.form.get(
            "max_income",
            ""
        ).strip()

        selected_percentage = request.form.get(
            "min_percentage",
            ""
        ).strip()


        # Apply filters
        filtered_df = apply_filters(
            df,
            selected_course,
            selected_category,
            selected_gender,
            selected_state,
            selected_income,
            selected_percentage
        )


        # Rank results
        if query:

            ranked_results = search_scholarships(
                query,
                filtered_df
            )

        else:

            ranked_results = filtered_df.head(10)


        # Prepare results for HTML
        for _, row in ranked_results.iterrows():

            if "final_score" in row:

                score = float(
                    row["final_score"]
                )

            else:

                score = 0.0


            score = max(
                0.0,
                min(1.0, score)
            )


            results.append({

                "name": display_value(
                    row[NAME_COLUMN]
                    if NAME_COLUMN
                    else "",
                    "Scholarship"
                ),

                "description": display_value(
                    row[DESCRIPTION_COLUMN]
                    if DESCRIPTION_COLUMN
                    else "",
                    "No description available."
                ),

                "provider": display_value(
                    row[PROVIDER_COLUMN]
                    if PROVIDER_COLUMN
                    else "",
                    "Not specified"
                ),

                "eligibility": display_value(
                    row[ELIGIBILITY_COLUMN]
                    if ELIGIBILITY_COLUMN
                    else "",
                    "Not specified"
                ),

                "amount": display_value(
                    row[AMOUNT_COLUMN]
                    if AMOUNT_COLUMN
                    else "",
                    "Not specified"
                ),

                "course": display_value(
                    row[COURSE_COLUMN]
                    if COURSE_COLUMN
                    else "",
                    ""
                ),

                "category": display_value(
                    row[CATEGORY_COLUMN]
                    if CATEGORY_COLUMN
                    else "",
                    ""
                ),

                "state": display_value(
                    row[STATE_COLUMN]
                    if STATE_COLUMN
                    else "",
                    ""
                ),

                "level": display_value(
                    row[LEVEL_COLUMN]
                    if LEVEL_COLUMN
                    else "",
                    ""
                ),

                "deadline": display_value(
                    row[DEADLINE_COLUMN]
                    if DEADLINE_COLUMN
                    else "",
                    "Not specified"
                ),

                "link": clean_url(
                    row[URL_COLUMN]
                    if URL_COLUMN
                    else ""
                ),

                "match_score": score
            })


    return render_template(
        "index.html",

        results=results,

        query=query,

        searched=searched,

        total_scholarships=len(df),

        course_values=course_values,

        category_values=category_values,

        gender_values=gender_values,

        state_values=state_values,

        selected_course=selected_course,

        selected_category=selected_category,

        selected_gender=selected_gender,

        selected_state=selected_state,

        selected_income=selected_income,

        selected_percentage=selected_percentage
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )