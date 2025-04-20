import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load movie data
movies = pd.read_csv('movies.csv')

# Ensure description exists (fill empty ones to avoid errors)
if 'description' not in movies.columns:
    movies['description'] = ''
movies['description'] = movies['description'].fillna('')

# Create a new column combining title and genres
movies['content'] = movies['title'] + ' ' + movies['genres']

# Vectorize the content
cv = CountVectorizer(stop_words='english')
content_matrix = cv.fit_transform(movies['content'])

# Compute similarity matrix
cosine_sim = cosine_similarity(content_matrix, content_matrix)

# Recommendation function (returns list of dicts: title + description)
def recommend(movie_title):
    idx_list = movies[movies['title'].str.lower() == movie_title.lower()].index

    if len(idx_list) == 0:
        return []  # Movie not found

    idx = idx_list[0]
    scores = list(enumerate(cosine_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    movie_indices = [i[0] for i in scores[1:6]]  # Top 5 excluding the selected movie

    recommended = movies.iloc[movie_indices][['title', 'description']]
    return recommended.to_dict(orient='records')
