<br/>
<p align="center">
  <h1 align="center">The Movie Cinema</h1>

  <p align="center">
    A Flask-based web application for discovering movies, getting recommendations, and reading sentiment-analyzed reviews.
    <br/>
    <br/>
    <a href="https://github.com/your_username/movie_rec/issues">Report Bug</a>
    .
    <a href="https://github.com/wintermoon707/movie_rec/issues">Request Feature</a>
  </p>
</p>



![Python](https://img.shields.io/badge/Python-3.8-blueviolet)
![Framework](https://img.shields.io/badge/Framework-Flask-red)
![Frontend](https://img.shields.io/badge/Frontend-HTML/CSS/JS-green)
![API](https://img.shields.io/badge/API-TMDB-fcba03)

## About The Project

**The Movie Cinema** is a comprehensive movie recommendation engine. This application provides all the details of a requested movie, such as its overview, genre, release date, rating, runtime, top cast, and similar movie recommendations.

A unique feature of this project is its sentiment analysis capability. Movie details are fetched from the TMDB API, and the application then uses the movie's IMDB ID to scrape user reviews from the IMDB website. These reviews are processed by a pre-trained NLP model to determine if the sentiment is positive or negative, providing users with a quick sentiment overview.

The front-end is designed to be user-friendly, with auto-suggestions to help you find movies as you type. If you can't find a movie in the suggestions, just type the full name and press enter; the search is robust enough to handle minor typos.

### Built With

This project utilizes a variety of modern technologies:

*   **Backend:**
    *   Python 3.8
    *   Flask
    *   Pandas & NumPy
*   **Machine Learning:**
    *   Scikit-learn
*   **Web Scraping:**
    *   Beautiful Soup
*   **Frontend:**
    *   HTML5 / CSS3
    *   JavaScript (ES6)
    *   jQuery
*   **APIs:**
    *   The Movie Database (OMDB) API

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

*   Python 3.8+ and Pip installed on your system.
*   A   OMDB API Key.

### Installation & Setup

1.  **Get a OMDB API Key**
    *   Create a free account at https://www.themoviedb.org/.
    *   In your account settings, click on the `API` link from the left-hand sidebar.
    *   Fill out the form to request an API key. You can enter "N/A" for the website URL if you don't have one.
    *   Once approved, your API key will be available in the `API` section.

2.  **Clone the repository**
    ```sh
    git clone https://github.com/wintermoon707/movie_rec.git
    cd movie_rwec
    ```

3.  **Install Python packages**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Add your API Key**
    *   Open the file `/static/recommend.js`.
    *   Replace `YOUR_API_KEY` on line 2 with the key you obtained from TMDB.
    ```javascript
    // static/recommend.js
    var myAPI = 'YOUR_API_KEY' // Replace this with your actual key
    ```

5.  **Run the application**
    ```sh
    python main.py
    ```

6.  **View the application**
    *   Open your web browser and go to `http://127.0.0.1:5000/`.

## Features

- **Movie Search**: Find movies with auto-suggestions.
- **Detailed Information**: Access movie overviews, genres, ratings, runtime, and posters.
- **Top Cast**: See the main actors for any movie.
- **Sentiment Analysis**: View scraped IMDB user reviews classified as "Positive" or "Negative".
- **Recommendations**: Get a list of movies similar to the one you're viewing.

## Data Sources

The machine learning model was trained on data aggregated from the following sources:

1.  IMDB 5000 Movie Dataset
2.  The Movies Dataset
3.  Wikipedia Lists of American films (2018-2020)
    *   2018 Films
    *   2019 Films
    *   2020 Films

