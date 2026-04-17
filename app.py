import streamlit as st
import pickle
import requests
import pandas as pd
import time

st.set_page_config(
    page_title="CineMatch – Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background-color: #0d0d0d; }
    h1 { color: #e50914; font-size: 2.8rem !important; }
    .movie-title {
        color: #ffffff;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 8px;
        text-align: center;
        min-height: 36px;
    }
    .stButton > button {
        background-color: #e50914;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover { background-color: #b20710; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    movies     = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()


TMDB_API_KEY = "90ea404f268b266ff026984b12c003cd"
BASE_IMG_URL = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER  = "https://placehold.co/300x450/1a1a1a/e50914?text=No+Poster"


def tmdb_get(url, retries=3):
    """
    Calls TMDB API safely:
    - Retries up to 3 times on failure
    - Waits 0.25s between calls to avoid rate limiting
    - Returns parsed JSON or empty dict on failure
    """
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 429:          # rate limited
                time.sleep(1)                    # wait 1 second and retry
                continue
            resp.raise_for_status()
            time.sleep(0.25)                     # gentle delay between calls
            return resp.json()
        except Exception:
            time.sleep(0.5 * (attempt + 1))      # backoff: 0.5s, 1s, 1.5s
    return {}

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id, title=""):
    data = tmdb_get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US")
    path = data.get("poster_path")
    if path:
        return BASE_IMG_URL + path

    if title:
        results = tmdb_get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}"
            f"&query={requests.utils.quote(title)}&language=en-US"
        ).get("results", [])
        for r in results:
            path = r.get("poster_path")
            if path:
                return BASE_IMG_URL + path

    return PLACEHOLDER


@st.cache_data(show_spinner=False)
def fetch_details(movie_id, title=""):
    def extract(d):
        return (
            round(d.get("vote_average", 0), 1) or None,
            d.get("overview") or "Overview unavailable.",
            [g["name"] for g in d.get("genres", [])][:3],
            (d.get("release_date") or "")[:4],
        )

    data = tmdb_get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US")
    if data.get("overview") or data.get("vote_average"):
        return extract(data)

    if title:
        results = tmdb_get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}"
            f"&query={requests.utils.quote(title)}&language=en-US"
        ).get("results", [])
        if results:
            data = tmdb_get(f"https://api.themoviedb.org/3/movie/{results[0]['id']}?api_key={TMDB_API_KEY}&language=en-US")
            return extract(data)

    return None, "Overview unavailable.", [], ""



def recommend(movie, n=10):
    index      = movies[movies["title"] == movie].index[0]
    distances  = similarity[index]
    top        = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:n+1]
    results    = []
    for i, score in top:
        row = movies.iloc[i]
        mid, title = row["id"], row["title"]
        results.append({
            "title":  title,
            "id":     mid,
            "score":  round(score * 100, 1),
            "poster": fetch_poster(mid, title),
        })
    return results

st.markdown("#  Movie Recommender System")
st.markdown("##### *AI-powered movie recommendations based on content similarity*")
st.divider()

c1, c2 = st.columns([4, 1])
with c1:
    selected_movie = st.selectbox("Movie", movies["title"].values, label_visibility="collapsed")
with c2:
    clicked = st.button("✨ Recommend")




if selected_movie:
    row    = movies[movies["title"] == selected_movie].iloc[0]
    sid    = int(row["id"])
    poster = fetch_poster(sid, selected_movie)
    rating, overview, genres, year = fetch_details(sid, selected_movie)

    ca, cb = st.columns([1, 4])
    with ca:
        st.image(poster, width=160)
    with cb:
        st.markdown(f"### {selected_movie}{' (' + year + ')' if year else ''}")
        if rating:
            st.markdown(f" **{rating} / 10**")
        if genres:
            st.markdown("  ".join([f"`{g}`" for g in genres]))
        if overview:
            st.caption(overview[:300] + ("..." if len(overview) > 300 else ""))
        else:
            st.caption("No description available for this movie.")

st.divider()


if clicked:
    with st.spinner("Finding your perfect movies..."):
        results = recommend(selected_movie, n=10)

    def render_row(items):
        cols = st.columns(5)
        for col, m in zip(cols, items):
            r, _, _, yr = fetch_details(m["id"], m["title"])
            with col:
                st.image(m["poster"], use_container_width=True)
                st.markdown(f"<div class='movie-title'>{m['title']}</div>", unsafe_allow_html=True)
                meta = []
                if r:  meta.append(f" {r}")
                if yr: meta.append(yr)
                if meta: st.caption("  ·  ".join(meta))

    st.markdown("###  Recommended For You")
    render_row(results[:5])
    st.markdown("###  More Picks")
    render_row(results[5:])

    with st.expander(" Similarity Scores"):
        st.dataframe(
            pd.DataFrame([{"Movie": r["title"], "Similarity (%)": r["score"]} for r in results]),
            use_container_width=True, hide_index=True
        )

st.divider()
st.markdown("<div style='text-align:center;color:#555;font-size:0.8rem;'>Built a Recommendation System using Streamlit · Data from TMDB</div>", unsafe_allow_html=True)


