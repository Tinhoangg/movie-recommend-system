#  Movie Recommendation System

##  Introduction
This is a **Movie Recommendation System** built with Python.  
It suggests movies to users using:
- **Content-based filtering** → recommends similar movies by description, cast, director, or genre.  
---

## 🛠 Tech Stack
- **Python 3.10+**
- **Pandas, NumPy** → data cleaning and processing
- **Jupyter Notebook** → exploration & experiments
- **Scikit-learn** → similarity calculation (content-based)
- **difflib** → fuzzy matching for movie title search
- **FastAPI** → build RESTful API
- **Uvicorn** → run API server

---
## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/Tinhoangg/movie-recommend-system.git
cd movie-recommend-system
```
### 2. Create virtual environment (optional)
```bash
python -m venv venv
# Activate venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```
###  3. Install dependencies
``` bash
pip install -r requirements.txt
```
### 4. Run the application
``` bash
python main.py
```
### 5. Open in Browser
Web interface: http://127.0.0.1:8001/
