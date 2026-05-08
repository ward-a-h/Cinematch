# CineMatch

A hybrid movie recommendation system built as a combined AI + Database Systems university project at FAST-NUCES, Spring 2026.

CineMatch takes a movie you like and your user ID, then returns 10 personalized recommendations using content-based filtering, collaborative filtering, and SVD. Results are displayed on a web interface with posters and ratings pulled from TMDB. The system is backed by a fully normalized SQLite database storing all users, movies, ratings, genres, and interaction logs from the MovieLens 100K dataset.

---

## What it does

- Enter a user ID and a movie you like → get 10 personalized recommendations with posters and star ratings
- Find Similar Movies → returns genre-similar movies regardless of user
- Every recommendation request is logged to the database with a timestamp

---

## How it works

The recommendation engine combines three approaches:

- **Content-based filtering** — represents each movie as a binary genre vector and finds similar ones using cosine similarity
- **Collaborative filtering** — finds the 50 most similar users and recommends movies they rated highly that you haven't seen
- **SVD** — matrix factorization that predicts ratings for unseen movies using 50 latent factors

Final score: **60% collaborative + 40% content-based**

---

## Database

The SQLite database (`cinematch.db`) stores the full MovieLens 100K dataset in a normalized 3NF schema across 6 tables:

| Table | Rows |
|---|---|
| users | 943 |
| movies | 1,682 |
| genres | 19 |
| movie_genres | 2,893 |
| ratings | 100,000 |
| interaction_logs | runtime |

See `DB component/DB_code.ipynb` for the full schema, ER diagram, and 8 SQL queries with results.

---

## Results

| Metric | Result |
|---|---|
| RMSE | 1.03 |
| MAE | 0.85 |
| Precision@10 | 0.50 |
| Recall@10 | 0.49 |
| Best K (collaborative) | 50 |

---

## Tech stack

Python, FastAPI, Streamlit, SQLite, scikit-learn, SciPy, pandas, TMDB API, MovieLens 100K

---

## Setup

```bash
pip install fastapi uvicorn streamlit requests pandas numpy scikit-learn scipy
```

1. Add your TMDB API key in `AI component/app.py`
2. Run the backend: `uvicorn app:app --reload`
3. Run the frontend: `streamlit run frontend.py`

The database is pre-populated. To rebuild it from scratch, run all cells in `DB component/DB_code.ipynb`.

---

## Repository structure

```
Cinematch/
├── AI component/    # FastAPI backend, Streamlit frontend, trained models, demo, ppt, report
├── DB component/    # SQLite database, Jupyter notebook, DB report
└── ml-100k/         # MovieLens 100K dataset
```
---

## Team

Tayaba (24K-0934), Wardah Ahmed (24K-1045), Humna Fatime (23K-1016)
FAST-NUCES — Spring 2026
