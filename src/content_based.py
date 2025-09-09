import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import difflib
class MovieRecommender:

    def __init__(self,path='data/netflix_titles_clean.csv'):
        self.df = pd.read_csv(path,encoding='latin-1')
        self.vectorize = None
        self.indices = None
        self.vector_matrix = None

    def preprocess_data(self):

        # transfer features to vector 
        self.vectorize = TfidfVectorizer(stop_words='english',max_features=10000)
        self.vector_matrix = self.vectorize.fit_transform(self.df['combined_feature'])
        
        # save movie index to indices
        self.df['title_lower'] = self.df['title'].str.lower().str.strip()
        self.indices = pd.Series(self.df.index, index=self.df['title_lower']).drop_duplicates()

    def find_title(self, title):
       all_titles = self.df['title_lower'].tolist()
       best_ratio = 0
       best_title = None

       for t in all_titles:
          if title in t:  # substring match 
            ratio = difflib.SequenceMatcher(None, title, t).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_title = t

       return best_title
    
    def content_based_filter(self, title,top=5):
       idx = self.indices[title]

       # calculate cosine similarity
       cosine_sim = linear_kernel(self.vector_matrix[idx], self.vector_matrix).flatten()
       sim_score = list(enumerate(cosine_sim))

       #sort similarity
       sim_score_sorted = sorted(sim_score, key=lambda x: x[1], reverse=True)
       sim_score_sorted = sim_score_sorted[1:top+1]
       # get top n movie recommend
       movie_index = [i[0] for i in sim_score_sorted]
       print(title)
       return self.df.iloc[movie_index][['title','description','director','cast','duration']]
     
