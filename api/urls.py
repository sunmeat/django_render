from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ArtistViewSet,
    AlbumViewSet,
    TrackViewSet,
    GenreViewSet,
)

router = DefaultRouter()

router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'tracks', TrackViewSet, basename='track')
router.register(r'genres', GenreViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls)),
]

# що автоматично створилось:

# Artists:
# GET    /api/v1/artists/
# POST   /api/v1/artists/
# GET    /api/v1/artists/{id}/
# PUT    /api/v1/artists/{id}/
# PATCH  /api/v1/artists/{id}/
# DELETE /api/v1/artists/{id}/

# Albums / Tracks / Genres — так само