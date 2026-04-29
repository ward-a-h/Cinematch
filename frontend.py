import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

TMDB_API_KEY = "003b359044adc636b66d5c783244390d"

@st.cache_data
def load_data():
    ratings = pd.read_csv('ml-100k/ml-100k/u.data',
                          sep='\t',
                          names=['user_id', 'movie_id', 'rating', 'timestamp'])
    ratings = ratings.drop('timestamp', axis=1)

    genre_columns = ['unknown', 'Action', 'Adventure', 'Animation', 'Childrens',
                     'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
                     'FilmNoir', 'Horror', 'Musical', 'Mystery', 'Romance',
                     'SciFi', 'Thriller', 'War', 'Western']

    movies = pd.read_csv('ml-100k/ml-100k/u.item',
                         sep='|',
                         encoding='latin-1',
                         names=['movie_id', 'movie_title', 'release_date', 'video_date',
                                'imdb_url'] + genre_columns)
    movies = movies[['movie_id', 'movie_title'] + genre_columns]

    genre_matrix = movies[genre_columns].values
    cosine_sim = cosine_similarity(genre_matrix)

    user_movie_matrix = ratings.pivot_table(index='user_id', columns='movie_id', values='rating')
    matrix_filled = user_movie_matrix.fillna(0)
    user_similarity = cosine_similarity(matrix_filled)
    user_similarity_df = pd.DataFrame(user_similarity,
                                      index=user_movie_matrix.index,
                                      columns=user_movie_matrix.index)

    movies['display_title'] = movies['movie_title'].str.replace(r'\s*\(\d{4}\)', '', regex=True)

    return ratings, movies, cosine_sim, user_movie_matrix, user_similarity_df

def get_poster(movie_title):
    try:
        title = movie_title.split('(')[0].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data['results']:
            poster_path = data['results'][0]['poster_path']
            rating = round(data['results'][0]['vote_average'], 1)
            if poster_path:
                return f"https://image.tmdb.org/t/p/w300{poster_path}", rating
    except:
        pass
    return None, None

def get_hybrid_recommendations(user_id, movie_title, movies, cosine_sim, user_movie_matrix, user_similarity_df, num=10):
    if movie_title not in movies['movie_title'].values:
        return []

    idx = movies[movies['movie_title'] == movie_title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]

    content_scores = {}
    for i, score in sim_scores:
        mid = movies.iloc[i]['movie_id']
        content_scores[mid] = score

    if user_id not in user_movie_matrix.index:
        top = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)[:num]
        return movies[movies['movie_id'].isin([m for m, s in top])]['movie_title'].tolist()

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

    max_cf = max(cf_scores.values()) if cf_scores else 1
    max_cb = max(content_scores.values()) if content_scores else 1

    hybrid_scores = {}
    all_movies = set(content_scores.keys()) | set(cf_scores.keys())
    for mid in all_movies:
        if mid not in watched:
            cb = content_scores.get(mid, 0) / max_cb
            cf = cf_scores.get(mid, 0) / max_cf
            hybrid_scores[mid] = 0.6 * cf + 0.4 * cb

    top = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:num]
    return movies[movies['movie_id'].isin([m for m, s in top])]['movie_title'].tolist()

def get_similar_movies(movie_title, movies, cosine_sim, num=10):
    if movie_title not in movies['movie_title'].values:
        return []
    idx = movies[movies['movie_title'] == movie_title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:num+1]
    movie_indices = [i[0] for i in sim_scores]
    return movies['movie_title'].iloc[movie_indices].tolist()

# Load data
with st.spinner("Loading CineMatch..."):
    ratings, movies, cosine_sim, user_movie_matrix, user_similarity_df = load_data()

title_mapping = dict(zip(movies['display_title'], movies['movie_title']))
display_titles = sorted(movies['display_title'].tolist())

st.title("CineMatch - Movie Recommendation System")
st.write("Get personalized movie recommendations!")

st.subheader("Get Recommendations")
st.write("Enter your user ID and pick a movie you enjoy. Our hybrid algorithm combines your taste with genre similarity to recommend 10 movies you have not seen yet. Results will vary by user.")

user_id = st.number_input("Enter your User ID (1-943)", min_value=1, max_value=943, value=1)
selected = st.selectbox("Search for a movie you like", [""] + display_titles)
movie_title = title_mapping.get(selected, "")

if st.button("Get Recommendations"):
    if movie_title:
        with st.spinner("Finding recommendations..."):
            recs = get_hybrid_recommendations(user_id, movie_title, movies, cosine_sim, user_movie_matrix, user_similarity_df)
        if recs:
            st.subheader("We recommend:")
            cols = st.columns(5)
            for i, title in enumerate(recs):
                with cols[i % 5]:
                    poster, rating = get_poster(title)
                    if poster:
                        st.image(poster, use_container_width=True)
                    else:
                        st.write("🎬")
                    st.caption(f"**{title.split('(')[0].strip()}**")
                    if rating:
                        st.caption(f"⭐ {rating}/10")
    else:
        st.warning("Please select a movie!")

st.divider()

st.subheader("Find Similar Movies")
st.write("Pick any movie and we will find the 10 most similar ones based on genre. This is not personalized — everyone gets the same results for the same movie.")

selected2 = st.selectbox("Search for a movie", [""] + display_titles, key="similar")
similar_title = title_mapping.get(selected2, "")

if st.button("Find Similar"):
    if similar_title:
        with st.spinner("Finding similar movies..."):
            recs = get_similar_movies(similar_title, movies, cosine_sim)
        if recs:
            st.subheader("Similar movies:")
            cols = st.columns(5)
            for i, title in enumerate(recs):
                with cols[i % 5]:
                    poster, rating = get_poster(title)
                    if poster:
                        st.image(poster, use_container_width=True)
                    else:
                        st.write("🎬")
                    st.caption(f"**{title.split('(')[0].strip()}**")
                    if rating:
                        st.caption(f"⭐ {rating}/10")
    else:
        st.warning("Please select a movie!")