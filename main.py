from src import MovieRecommender
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import uvicorn

#  FastAPI 
app = FastAPI()
template = Jinja2Templates(directory='templates')

#  load MovieRecommender 
movie_recommender = MovieRecommender()
movie_recommender.preprocess_data()
movie_recommender.build_nn_model()


#  Routes 
@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return template.TemplateResponse('index.html', {'request': request})

@app.get('/recommend', response_class=HTMLResponse)
def recommend(request: Request, title: str = Query(..., description='Movie title to search')):
    match_title = movie_recommender.find_title(title)
    if match_title is None:
        return {"error": f"No movie found for '{title}'"}

    recommendations = movie_recommender.recommend_hybrid(match_title, top=5)
    rec_list = recommendations.to_dict(orient="records")

    return template.TemplateResponse(
        'recommend.html',
        {
            'request': request,
            'title': match_title,
            'recommendations': rec_list
        }
    )


