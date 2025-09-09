from src import MovieRecommender
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
template = Jinja2Templates(directory='templates')
movie_recommender = MovieRecommender()
movie_recommender.preprocess_data()

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
   return template.TemplateResponse('index.html', {'request': request})

@app.get('/recommend', response_class=HTMLResponse)
def recommend(request: Request, title: str = Query(...,description='movie title to search')):
   match_title = movie_recommender.find_title(title)
   recommed_movie = movie_recommender.content_based_filter(match_title)
   
   recommendations = recommed_movie.to_dict(orient="records")
   return template.TemplateResponse('recommend.html', {'request': request,
                                                   'title':match_title, 
                                                   'recommendations': recommendations
                                                   })