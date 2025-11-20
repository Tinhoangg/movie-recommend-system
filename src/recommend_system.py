import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Embedding, Flatten, Concatenate
from tensorflow.keras.models import Model

class MovieRecommender:

    def __init__(self, path='data/netflix_titles_clean.csv'):
        self.df = pd.read_csv(path, encoding='latin-1')
        self.vectorize = None
        self.indices = None
        self.vector_matrix = None
        self.nn_model = None

    #  Preprocess content 
    def preprocess_data(self):
        self.vectorize = TfidfVectorizer(stop_words='english', max_features=10000)
        self.vector_matrix = self.vectorize.fit_transform(self.df['combined_feature'])
        self.df['title_lower'] = self.df['title'].str.lower().str.strip()
        self.indices = pd.Series(self.df.index, index=self.df['title_lower']).drop_duplicates()

    #  Find closest title 
    def find_title(self, title):
        all_titles = self.df['title_lower'].tolist()
        matches = difflib.get_close_matches(title.lower(), all_titles, n=1, cutoff=0.5)
        return matches[0] if matches else None

    #  Content-based filter 
    def content_based_filter(self, title, top=5):
        idx = self.indices[title]
        cosine_sim = cosine_similarity(self.vector_matrix[idx], self.vector_matrix).flatten()
        sim_score = list(enumerate(cosine_sim))
        sim_score_sorted = sorted(sim_score, key=lambda x: x[1], reverse=True)[1:top+1]
        movie_index = [i[0] for i in sim_score_sorted]
        return self.df.iloc[movie_index][['title','description','director','cast','duration']]

    #  Neural Network 
    def build_nn_model(self, embedding_dim=64):
        movie_input = Input(shape=(1,), name='movie_input')
        movie_emb = Embedding(input_dim=len(self.df), output_dim=embedding_dim)(movie_input)
        movie_emb_flat = Flatten()(movie_emb)
        feature_input = Input(shape=(self.vector_matrix.shape[1],), name='feature_input')
        x = Concatenate()([movie_emb_flat, feature_input])
        x = Dense(128, activation='relu')(x)
        x = Dense(64, activation='relu')(x)
        output = Dense(1, activation='sigmoid')(x)
        self.nn_model = Model(inputs=[movie_input, feature_input], outputs=output)
        self.nn_model.compile(optimizer='adam', loss='mse')

    #  Train NN 
    def train_nn(self, movie_indices, feature_vectors, target_scores, epochs=20, batch_size=32):
        self.nn_model.fit(
            [movie_indices, feature_vectors],
            target_scores,
            epochs=epochs,
            batch_size=batch_size
        )

    #  Recommend hybrid (Content + NN) 
    def recommend_hybrid(self, title, top=5):
        idx = self.indices[title]
        feature_vec = self.vector_matrix[idx].toarray()

        # Lấy top 20 từ content-based làm candidate
        top_movies = self.content_based_filter(title, top=20)
        top_indices = [self.indices[t.lower()] for t in top_movies['title']]

        # Dự đoán score NN
        feature_batch = np.repeat(feature_vec, len(top_indices), axis=0)
        scores = self.nn_model.predict([np.array(top_indices), feature_batch], verbose=0)
        top_idx_sorted = np.argsort(scores[:,0])[::-1][:top]

        return self.df.iloc[top_indices].iloc[top_idx_sorted][['title','description','director','cast','duration']]


     
