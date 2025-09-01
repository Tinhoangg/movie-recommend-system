import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize
import difflib
path = 'movies_rating_dataset.csv'
df = pd.read_csv(path)
df = df.drop(columns=['timestamp'])

user_matrix = df.pivot(index='userId',columns='movieId',values='rating')
fill_matrix = user_matrix.fillna(0)

fill_matrix = normalize(fill_matrix,'l2')

user_sim = linear_kernel(fill_matrix, fill_matrix)
user_sim_df = pd.DataFrame(user_sim, index=user_matrix.index,columns=user_matrix.index)

def collaborative_filtering(userId,topn=5,top_user=5):

    #tim user giong nhat
    sim_users = user_sim_df[userId].sort_values(ascending=False).drop(userId).head(top_user)

    # lay nhung phim cua user giong nhat da xem
    seen_movies = df[df['userId'] == userId]['movieId'].tolist()
    candidates = df[(df['userId'].isin(sim_users.index)) &(~df['movieId'].isin(seen_movies))]

    # tính weighted rating
    candidates = candidates.merge(sim_users, left_on="userId", right_index=True)
    candidates['weighted_rating'] = candidates['rating'] * candidates[userId]
    
    recommend_movie = candidates.groupby(['movieId','title','genres']).agg(
        weighted_score=('weighted_rating','sum'),
        sim_sum=(userId,'sum'))
    recommend_movie['score'] = recommend_movie['weighted_score'] / recommend_movie['sim_sum']

    return recommend_movie.sort_values('score',ascending=False).head(topn)[['score']]
user_input = int(input('enter user id: '))
print(collaborative_filtering(user_input))
print(df[df['userId'] == user_input])
