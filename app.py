from fastapi import FastAPI
import pickle
import numpy as np
import pandas as pd
import requests

TMDB_API_KEY = "003b359044adc636b66d5c783244390d"

def get_poster(movie_title):
    try:
        # remove year from title for search
        title = movie_title.split('(')[0].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        response = requests.get(url)
        data = response.json()
        if data['results']:
            poster_path = data['results'][0]['poster_path']
            rating = round(data['results'][0]['vote_average'], 1)
            if poster_path:
                return f"https://image.tmdb.org/t/p/w300{poster_path}", rating
    except:
        pass
    return None, None

app = FastAPI()

# load all saved models
cosine_sim = pickle.load(open('cosine_sim.pkl', 'rb'))
user_similarity_df = pickle.load(open('user_similarity_df.pkl', 'rb'))
movies_full = pickle.load(open('movies_full.pkl', 'rb'))
movies = pickle.load(open('movies.pkl', 'rb'))
user_movie_matrix = pickle.load(open('user_movie_matrix.pkl', 'rb'))

genre_columns = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens',
                 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
                 'FilmNoir', 'Horror', 'Musical', 'Mystery', 'Romance',
                 'SciFi', 'Thriller', 'War', 'Western']

@app.get("/")
def home():
    return {"message": "CineMatch API is running!"}

@app.get("/recommend")
def recommend(movie_title: str, user_id: int):
    # content based scores
    if movie_title not in movies_full['movie_title'].values:
        return {"error": f"Movie '{movie_title}' not found!"}
    
    idx = movies_full[movies_full['movie_title'] == movie_title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]
    
    content_scores = {}
    for i, score in sim_scores:
        mid = movies_full.iloc[i]['movie_id']
        content_scores[mid] = score
    
    # collaborative scores
    if user_id not in user_movie_matrix.index:
        return {"error": f"User {user_id} not found!"}
    
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:51]
    watched = user_movie_matrix.loc[user_id].dropna().index.tolist()
    
    cf_scores = {}
    for similar_user, similarity in similar_users.items():
        similar_user_movies = user_movie_matrix.loc[similar_user].dropna()
        similar_user_movies = similar_user_movies[similar_user_movies >= 4]
        for mid, rating in similar_user_movies.items():
            if mid not in watched:
                if mid not in cf_scores:
                    cf_scores[mid] = 0
                cf_scores[mid] += similarity * rating
    
    # hybrid
    max_cf = max(cf_scores.values()) if cf_scores else 1
    max_cb = max(content_scores.values()) if content_scores else 1
    
    hybrid_scores = {}
    all_movies = set(content_scores.keys()) | set(cf_scores.keys())
    for mid in all_movies:
        if mid not in watched:
            cb = content_scores.get(mid, 0) / max_cb
            cf = cf_scores.get(mid, 0) / max_cf
            hybrid_scores[mid] = 0.6 * cf + 0.4 * cb
    
    top_movies = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    top_ids = [mid for mid, score in top_movies]
    result = movies[movies['movie_id'].isin(top_ids)]['movie_title'].tolist()
    
    recommendations_with_posters = []
    for title in result:
        poster, rating = get_poster(title)
        recommendations_with_posters.append({
            "title": title,
            "poster": poster,
            "rating": rating
        })
    
    return {"recommendations": recommendations_with_posters}
@app.get("/similar")
def similar(movie_title: str):
    if movie_title not in movies_full['movie_title'].values:
        return {"error": f"Movie '{movie_title}' not found!"}
    
    idx = movies_full[movies_full['movie_title'] == movie_title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    result = movies_full['movie_title'].iloc[movie_indices].tolist()
    
    similar_with_posters = []
    for title in result:
        poster, rating = get_poster(title)
        similar_with_posters.append({
            "title": title,
            "poster": poster,
            "rating": rating
        })
    
    return {"similar_movies": similar_with_posters}