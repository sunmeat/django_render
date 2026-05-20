from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home_redirect, name='home'), 

    # виконавці
    path('artists/', views.ArtistListView.as_view(), name='artist-list'),
    path('artists/<int:pk>/', views.ArtistDetailView.as_view(), name='artist-detail'),

    # альбоми
    path('albums/', views.AlbumListView.as_view(), name='album-list'),
    path('albums/<int:pk>/', views.AlbumDetailView.as_view(), name='album-detail'),

    # треки
    path('tracks/', views.TrackListView.as_view(), name='track-list'),
    path('tracks/<int:pk>/', views.TrackDetailView.as_view(), name='track-detail'),
]