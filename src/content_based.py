import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import difflib
#read data
path = 'data/netflix_titles_clean.csv'
df = pd.read_csv(path,encoding='latin-1')

# transfer features to vector 
vectorize = TfidfVectorizer(stop_words='english',max_features=10000)
vector_matrix = vectorize.fit_transform(df['combined_feature'])

# save movie index to indices
df['title_lower'] = df['title'].str.lower().str.strip()
indices = pd.Series(df.index, index=df['title_lower']).drop_duplicates()

def content_based_filter(title,top=5):
    idx = indices[title]

    # calculate cosine similarity
    cosine_sim = linear_kernel(vector_matrix[idx], vector_matrix).flatten()
    sim_score = list(enumerate(cosine_sim))

    #sort similarity
    sim_score_sorted = sorted(sim_score, key=lambda x: x[1], reverse=True)
    sim_score_sorted = sim_score_sorted[1:top+1]
    # get top n movie recommend
    movie_index = [i[0] for i in sim_score_sorted]

    return df.iloc[movie_index][['title','description','director','cast','duration']]
def find_title(title):
    all_titles = df['title_lower'].tolist()
    best_ratio = 0
    best_title = None

    for t in all_titles:
        if title in t:  # substring match 
            ratio = difflib.SequenceMatcher(None, title, t).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_title = t

    return best_title



if __name__ == "__main__":  
   name = input('enter name: ').lower().strip()

   # find closest movie name from data that match input
   closest_match = find_title(name)
   
   if closest_match:
       print(closest_match)
       print(content_based_filter(closest_match))
   else:
       print('cant find movie name')
