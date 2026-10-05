# ScholarFind

ScholarFind is an Information Retrieval-based scholarship search and ranking
system that helps students find relevant scholarship opportunities using
natural-language queries and eligibility filters.

## Features

- Natural-language scholarship search
- TF-IDF based document representation
- Cosine similarity based retrieval
- Keyword and title matching
- Scholarship ranking
- Course, category, gender and state filters
- Maximum family income filter
- Minimum percentage filter
- Top 10 ranked scholarship results
- Official application links

## Tech Stack

- Python
- Flask
- Pandas
- Scikit-learn
- HTML
- CSS
- JavaScript
- CSV

## Information Retrieval

ScholarFind uses the Vector Space Model with TF-IDF weighting.

The system:

1. Loads scholarship records from a CSV file.
2. Combines textual scholarship fields into searchable text.
3. Converts scholarship records into TF-IDF vectors.
4. Converts the user's query into a TF-IDF vector.
5. Calculates cosine similarity between the query and scholarships.
6. Calculates keyword and title matching scores.
7. Combines the scores to rank scholarships.
8. Returns the top 10 results.

Final Score:

0.70 × TF-IDF Score
+ 0.20 × Keyword Score
+ 0.10 × Title Score

## Dataset

The project contains 159 scholarship records with 18 original fields.

## Project Structure

ScholarFind/
├── app.py
├── dataset/
│   └── scholarships.csv
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── requirements.txt
└── README.md

## How to Run

Install the dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Then open the local Flask URL in your browser.

## Project Objective

The objective is to demonstrate an end-to-end Information Retrieval
pipeline for scholarship discovery, including document preparation,
vector representation, query processing, similarity calculation,
ranking and result presentation.