import socket

import httpx

from app.core.config import TMDB_API_KEY


original_getaddrinfo = socket.getaddrinfo


def force_ipv4(*args, **kwargs):
    responses = original_getaddrinfo(*args, **kwargs)

    return [
        response
        for response in responses
        if response[0] == socket.AF_INET
    ]


socket.getaddrinfo = force_ipv4


class TMDBClient:

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):

        self.client = httpx.Client(
            timeout=90.0,
            follow_redirects=True,
        )

    def search_movies(
        self,
        query: str
    ):

        url = f"{self.BASE_URL}/search/movie"

        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
        }

        response = self.client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()

    def get_movie_details(
        self,
        movie_id: int
    ):

        url = f"{self.BASE_URL}/movie/{movie_id}"

        params = {
            "api_key": TMDB_API_KEY,
        }

        response = self.client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()