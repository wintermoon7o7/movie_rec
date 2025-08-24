import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
from datetime import date, datetime

# load the nlp model and tfidf vectorizer from disk
try:
    filename = 'nlp_model.pkl'
    clf = pickle.load(open(filename, 'rb'))
    vectorizer = pickle.load(open('tranform.pkl','rb'))
except FileNotFoundError:
    print("Model files not found. Please ensure nlp_model.pkl and tranform.pkl are in the root directory.")
    clf = None
    vectorizer = None

# ---- Recommendation model ----
def create_similarity():
    data = pd.read_csv('main_data.csv')
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'].fillna(''))
    # creating a similarity score matrix
    similarity = cosine_similarity(count_matrix)
    return data, similarity

def rcmd(m, data, similarity):
    m = m.lower()
    if m not in data['movie_title'].unique():
        return([])
    i = data.loc[data['movie_title']==m].index[0]
    lst = list(enumerate(similarity[i]))
    lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
    lst = lst[1:11] # excluding first item since it is the requested movie itself
    l = []
    for i in range(len(lst)):
        a = lst[i][0]
        l.append(data['movie_title'][a])
    return l

# Pre-load the recommendation model data
rec_data, rec_similarity = create_similarity()
# ---- End of recommendation model ----

def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

app = Flask(__name__)
suggestions = get_suggestions()

@app.route("/")
@app.route("/home")
def home():    
    return render_template('home.html', suggestions=suggestions)

@app.route("/skeleton")
def skeleton():
    return render_template('skeleton.html')

@app.route("/populate-matches",methods=["POST"])
def populate_matches():
    # getting data from AJAX request
    res = json.loads(request.get_data("data"));
    movies_list = res['movies_list'];
    
    # OMDb search results have a different structure
    movie_cards = {
        movies_list[i]['Poster'] if movies_list[i]['Poster'] != 'N/A' else "/static/default.jpg": [
            movies_list[i]['Title'],
            movies_list[i]['Title'], # OMDb doesn't provide original_title in search
            'N/A', # OMDb doesn't provide rating in search
            movies_list[i]['Year'],
            movies_list[i]['imdbID'] # Use imdbID for the next call
        ] for i in range(len(movies_list))
    }
    
    return render_template('recommend.html',movie_cards=movie_cards);



@app.route("/recommend",methods=["POST"])
def recommend():
    # getting data from AJAX request
    title = request.form.get('title')
    imdb_id = request.form.get('imdb_id')
    poster = request.form.get('poster')
    genres = request.form.get('genres')
    overview = request.form.get('overview')
    vote_average = request.form.get('rating')
    vote_count = request.form.get('vote_count')
    rel_date = request.form.get('rel_date')
    release_date = request.form.get('release_date')
    runtime = request.form.get('runtime')
    status = request.form.get('status')
    api_key = request.form.get('api_key')

    # get recommendations
    rec_movies = rcmd(title, rec_data, rec_similarity)
    rec_posters = []
    rec_ids = []
    rec_movies_org = []
    rec_year = []
    rec_vote = []

    for movie_title in rec_movies:
        try:
            url = "http://www.omdbapi.com/?t={}&apikey={}".format(movie_title.replace(" ", "+"), api_key)
            response = requests.get(url)
            movie_data = response.json()
            if movie_data.get('Response') == 'True':
                rec_posters.append(movie_data.get('Poster'))
                rec_ids.append(movie_data.get('imdbID'))
                rec_movies_org.append(movie_data.get('Title'))
                rec_year.append(movie_data.get('Year'))
                rec_vote.append(movie_data.get('imdbRating'))
            else:
                rec_posters.append('/static/default.jpg')
                rec_ids.append(movie_title) # use title as fallback id
                rec_movies_org.append(movie_title)
                rec_year.append('N/A')
                rec_vote.append('N/A')
        except:
            rec_posters.append('/static/default.jpg')
            rec_ids.append(movie_title) # use title as fallback id
            rec_movies_org.append(movie_title)
            rec_year.append('N/A')
            rec_vote.append('N/A')
    
    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: [rec_movies[i],rec_movies_org[i],rec_vote[i],rec_year[i],rec_ids[i]] for i in range(len(rec_posters))}

    # Try to get detailed cast info from TMDB
    try:
        cast_ids = json.loads(request.form.get('cast_ids'))
        cast_names = json.loads(request.form.get('cast_names'))
        cast_chars = json.loads(request.form.get('cast_chars'))
        cast_bdays = json.loads(request.form.get('cast_bdays'))
        cast_bios = json.loads(request.form.get('cast_bios'))
        cast_places = json.loads(request.form.get('cast_places'))
        cast_profiles = json.loads(request.form.get('cast_profiles'))

        casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}
        cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}
    except (TypeError, KeyError):
        # Fallback to simple actor list from OMDb if TMDB data is not available
        actors = json.loads(request.form.get('actors', '[]'))
        casts = {actor:[] for actor in actors}
        cast_details = {}

    movie_reviews = {}
    if imdb_id and clf and vectorizer:
        try:
            # web scraping to get user reviews from IMDB site
            sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
            soup = bs.BeautifulSoup(sauce,'lxml')
            soup_result = soup.find_all("div",{"class":"text show-more__control"})

            reviews_list = [] # list of reviews
            reviews_status = [] # list of comments (good or bad)
            for reviews in soup_result:
                if reviews.string:
                    reviews_list.append(reviews.string)
                    # passing the review to our model
                    movie_review_list = np.array([reviews.string])
                    movie_vector = vectorizer.transform(movie_review_list)
                    pred = clf.predict(movie_vector)
                    reviews_status.append('Positive' if pred else 'Negative')
            
            # combining reviews and comments into a dictionary
            movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}
        except Exception as e:
            print(e)

    # getting current date
    try:
        movie_rel_date = datetime.strptime(rel_date, '%d %b %Y')
    except (ValueError, TypeError):
        movie_rel_date = None
    curr_date = date.today() if movie_rel_date else None

    # passing all the data to the html file
    return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
        vote_count=vote_count,release_date=release_date,movie_rel_date=movie_rel_date,curr_date=curr_date,runtime=runtime,status=status,genres=genres,movie_cards=movie_cards,reviews=movie_reviews,casts=casts,cast_details=cast_details, suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)
