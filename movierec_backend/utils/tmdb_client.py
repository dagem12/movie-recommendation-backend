import requests
from django.conf import settings

class TMDbClient:
    BASE_URL = 'https://api.themoviedb.org/3'

    def __init__(self):
        self.api_key = settings.TMDB_API_KEY

    def _get(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_trending_movies(self, time_window='day'):
        return self._get(f"trending/movie/{time_window}")

    def get_movie_details(self, movie_id):
        return self._get(f"movie/{movie_id}")

    def search_movies(self, query):
        return self._get("search/movie", params={'query': query})