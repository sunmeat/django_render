from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from api.models import Artist, Album, Track


def home_redirect(request):
    """Перенаправляє на сторінку виконавців"""
    return redirect('app:artist-list')


class BaseView:
    """Базовий клас для передачі даних у sidebar"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_artists'] = Artist.objects.all()
        context['all_albums'] = Album.objects.select_related('artist').all()
        context['all_tracks'] = Track.objects.select_related('album').prefetch_related('artists').all()
        return context


class ArtistListView(BaseView, ListView):
    model = Artist
    template_name = 'app/artists/list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'artists'
        context['title'] = 'Виконавці'
        return context


class ArtistDetailView(BaseView, DetailView):
    model = Artist
    template_name = 'app/artists/detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'artists'
        context['title'] = 'Виконавець'
        context['albums'] = self.object.albums.all().order_by('-release_date')
        context['tracks'] = self.object.tracks.all()
        return context


class AlbumListView(BaseView, ListView):
    model = Album
    template_name = 'app/albums/list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'albums'
        context['title'] = 'Альбоми'
        return context


class AlbumDetailView(BaseView, DetailView):
    model = Album
    template_name = 'app/albums/detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'albums'
        context['title'] = 'Альбом'
        context['tracks'] = self.object.tracks.all().order_by('track_number', 'title')
        return context


class TrackListView(BaseView, ListView):
    model = Track
    template_name = 'app/tracks/list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'tracks'
        context['title'] = 'Треки'
        return context


class TrackDetailView(BaseView, DetailView):
    model = Track
    template_name = 'app/tracks/detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'tracks'
        context['title'] = 'Трек'
        return context