# CineMatch 
An AI-powered movie recommendation system built as a university project for FAST-NUCES.

CineMatch takes a movie you like and your user ID, then recommends 10 personalized movies using a combination of content-based filtering, collaborative filtering, and SVD. Results are displayed on a clean web interface with movie posters and ratings pulled from TMDB.

## What it does

You open the app, search for a movie you like, enter your user ID, and get 10 recommended movies with posters and star ratings. There is also a "Find Similar Movies" section that returns movies with similar genres.

## How it works

The recommendation engine uses three approaches and combines them. Content-based filtering looks at movie genres and finds similar ones using cosine similarity. Collaborative filtering finds users with similar taste to you and recommends what they liked. SVD is a matrix factorization technique that predicts what rating you would give to movies you have not seen. The final recommendation is a weighted combination of collaborative and content scores (60% collaborative, 40% content-based).

## Tech stack

Python, FastAPI, Streamlit, scikit-learn, scipy, pandas, TMDB API, MovieLens 100K dataset

## Results

RMSE: 1.03, MAE: 0.85, Precision@10: 0.50, Recall@10: 0.49

## Setup

Install dependencies:
pip install fastapi uvicorn streamlit requests pandas numpy scikit-learn scipy

Add your TMDB API key in app.py

Run the backend:
uvicorn app:app --reload

Run the frontend in a separate terminal:
streamlit run frontend.py

## Team
Tayaba (24K-0934), Wardah Ahmed (24K-1045), Humna Fatime (23K-1016)
FAST-NUCES, Spring 2026

Tayaba (24K-0934), Wardah Ahmed (24K-1045), Humna Fatime (23K-1016)
FAST-NUCES, Spring 2026
