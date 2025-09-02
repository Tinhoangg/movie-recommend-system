import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import normalize
import difflib
path = 'data/movies_rating_dataset.csv'
df = pd.read_csv(path)
df = df.drop(columns=['timestamp'])
#make user matrix and fill rating value = 0 to movie that user dont watch
user_matrix = df.pivot(index='userId',columns='movieId',values='rating')
fill_matrix = user_matrix.fillna(0)
#normalize matrix with l2 to use linear kernel
fill_matrix = normalize(fill_matrix,'l2')
# calculate similarity between user in matrix 
user_sim = linear_kernel(fill_matrix, fill_matrix)
user_sim_df = pd.DataFrame(user_sim, index=user_matrix.index,columns=user_matrix.index)

def collaborative_filtering(Id,topn=5,top_user=5):

    #find the most similar user
    sim_users = user_sim_df[Id].sort_values(ascending=False).drop(Id).head(top_user)

    # take movie from similar user and check if candidates saw it or not
    seen_movies = df[df['userId'] == Id]['movieId'].tolist()
    candidates = df[(df['userId'].isin(sim_users.index)) &(~df['movieId'].isin(seen_movies))]

    # calculate weighted rating
    candidates = candidates.merge(sim_users.rename('similarity'), left_on="userId", right_index=True)
    candidates['weighted_rating'] = candidates['rating'] * candidates['similarity']

    recommend_movie = candidates.groupby(['movieId','title','genres']).agg(
        weighted_score=('weighted_rating','sum'),
        sim_sum=('similarity', 'sum'))
    recommend_movie['score'] = recommend_movie['weighted_score'] / recommend_movie['sim_sum']

    return recommend_movie.reset_index().sort_values('score', ascending=False)[['movieId', 'title', 'genres']].head(topn)
if __name__ == "__main__":
    user_input = int(input('enter user id: '))
    
    recommend = collaborative_filtering(user_input)

    print(f'Movies Recommend: \n {recommend}')
