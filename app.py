from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import requests
import os
import gdown

app = Flask(__name__)

import os
import gdown

MOVIE_PIVOT_URL = "https://drive.google.com/uc?id=1vu6qcc4SctbW2NuMhuhfYP4bjbyaBeH3"
SIMILARITY_URL = "https://drive.google.com/uc?id=1MAGYsforbrsXiTyX9sRpBKtu68_x6xER"

if not os.path.exists("movie_pivot.pkl"):
    print("Downloading movie_pivot.pkl...")
    gdown.download(
        MOVIE_PIVOT_URL,
        "movie_pivot.pkl",
        quiet=False
    )

if not os.path.exists("similarity.pkl"):
    print("Downloading similarity.pkl...")
    gdown.download(
        SIMILARITY_URL,
        "similarity.pkl",
        quiet=False
    )

movie_pivot = pickle.load(open('movie_pivot.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.read_csv("dataset/movies.csv")
links = pd.read_csv("dataset/links.csv")

movies = movies.merge(
    links[['movieId', 'tmdbId']],
    on='movieId'
)

API_KEY = "dfb141bf55e1329e06a63bf87dddff38"

def fetch_poster(tmdb_id):

    try:

        if pd.isna(tmdb_id):
            return "/static/no-poster.png"

        url = f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}?api_key={API_KEY}"

        response = requests.get(url, timeout=10)

        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"

    except Exception as e:
        print(e)

    return "/static/no-poster.png"

def recommend(movie_name):

    index = np.where(
        movie_pivot.index == movie_name
    )[0][0]

    similar_movies = sorted(
        list(enumerate(similarity_scores[index])),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []

    for movie in similar_movies:
        title = movie_pivot.index[movie[0]]
        movie_row = movies[
            movies['title'] == title
        ]

        if len(movie_row) > 0:
            tmdb_id = movie_row.iloc[0]['tmdbId']

            recommendations.append({
                "title": title,
                "poster": fetch_poster(tmdb_id)
            })

    return recommendations

@app.route("/", methods=["GET", "POST"])
def home():

    recommendations = []

    if request.method == "POST":

        movie = request.form["movie"]

        recommendations = recommend(movie)

    return render_template(
        "index.html",
        movies=sorted(movie_pivot.index),
        recommendations=recommendations
    )

if __name__ == "__main__":
    app.run(debug=True)