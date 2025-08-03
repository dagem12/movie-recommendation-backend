from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.tmdb_client import TMDbClient

class TrendingMoviesView(APIView):
    def get(self, request):
        client = TMDbClient()
        data = client.get_trending_movies()
        return Response(data)
# Create your views here.
