import streamlit as st
import requests
import pickle

movies = pickle.load(open('movies.pkl', 'rb'))
movies['display_title'] = movies['movie_title'].str.replace(r'\s*\(\d{4}\)', '', regex=True)
title_mapping = dict(zip(movies['display_title'], movies['movie_title']))
display_titles = sorted(movies['display_title'].tolist())

st.title("CineMatch - Movie Recommendation System")
st.write("Get personalized movie recommendations!")

st.subheader("Get Recommendations")
user_id = st.number_input("Enter your User ID (1-943)", min_value=1, max_value=943, value=1)
selected = st.selectbox("Search for a movie you like", [""] + display_titles)
movie_title = title_mapping.get(selected, "")

if st.button("Get Recommendations"):
    if movie_title:
        with st.spinner("Finding recommendations..."):
            response = requests.get("http://127.0.0.1:8000/recommend",
                                    params={"movie_title": movie_title, "user_id": user_id})
            data = response.json()
        if "error" in data:
            st.error(data["error"])
        else:
            st.subheader("We recommend:")
            cols = st.columns(5)
            for i, movie in enumerate(data["recommendations"]):
                with cols[i % 5]:
                    if movie["poster"]:
                        st.image(movie["poster"], use_container_width=True)
                    else:
                        st.write("🎬")
                    st.caption(f"**{movie['title'].split('(')[0].strip()}**")
                    if movie["rating"]:
                        st.caption(f"⭐ {movie['rating']}/10")
    else:
        st.warning("Please select a movie!")

st.divider()

st.subheader("Find Similar Movies")
selected2 = st.selectbox("Search for a movie", [""] + display_titles, key="similar")
similar_title = title_mapping.get(selected2, "")

if st.button("Find Similar"):
    if similar_title:
        with st.spinner("Finding similar movies..."):
            response = requests.get("http://127.0.0.1:8000/similar",
                                    params={"movie_title": similar_title})
            data = response.json()
        if "error" in data:
            st.error(data["error"])
        else:
            st.subheader("Similar movies:")
            cols = st.columns(5)
            for i, movie in enumerate(data["similar_movies"]):
                with cols[i % 5]:
                    if movie["poster"]:
                        st.image(movie["poster"], use_container_width=True)
                    else:
                        st.write("🎬")
                    st.caption(f"**{movie['title'].split('(')[0].strip()}**")
                    if movie["rating"]:
                        st.caption(f"⭐ {movie['rating']}/10")
    else:
        st.warning("Please select a movie!")