from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

# Carregar os dados
filmes = pd.read_csv('Filmes.csv', sep=',')
ratings = pd.read_csv('Ratings.csv', sep=';')
dados = pd.read_csv('Dados.csv')
tags = pd.read_csv('Tags.csv')

# Preparar os dados para Content-Based Filtering
filmes['movieId'] = filmes['movieId'].apply(lambda x: str(x))
df2 = filmes.merge(dados, left_on='title', right_on='Name', how='left')
df2 = df2.merge(tags, left_on='movieId', right_on='movieId', how='left')
df2['Infos'] = df2['genres'] + str(df2['Directors_Cast']) + str(df2['Discription']) + df2['tag']

vec = TfidfVectorizer()
tfidf = vec.fit_transform(df2['Infos'].apply(lambda x: np.str_(x)))

sim = cosine_similarity(tfidf)
sim_df2 = pd.DataFrame(sim, columns=df2['title'], index=df2['title'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations')
def recommendations():
    title = request.args.get('title')
    if title in sim_df2.index:
        recommendations = pd.DataFrame(sim_df2[title].sort_values(ascending=False)).head(5)
        recommendations = recommendations.index.to_list()
        response = []
        for rec in recommendations:
            movie_info = df2[df2['title'] == rec].iloc[0]
            response.append({
                'title': rec,
                'poster': movie_info.get('poster_path', 'default.jpg'),
                'genres': movie_info.get('Tags', 'Popular')[2:],
                'synopsis': movie_info.get('Discription', 'Sinopse não disponível.')[2:]
            })
        return jsonify({'recommendations': response})
    else:
        return jsonify({'recommendations': []})


if __name__ == '__main__':
    app.run(debug=True)
