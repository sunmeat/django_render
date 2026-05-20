# python manage.py createsuperuser
# http://localhost:63786/admin/

from django.contrib import admin
from .models import Artist, Album, Track, Genre


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'created_at']
    list_filter = ['country']
    search_fields = ['name', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class TrackInline(admin.TabularInline):
    model = Track
    extra = 0
    fields = ['track_number', 'title', 'duration', 'is_explicit']
    show_change_link = True


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'release_date']
    list_filter = ['release_date', 'genres']
    search_fields = ['title', 'artist__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['genres']
    inlines = [TrackInline]


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'track_number', 'get_duration_display', 'is_explicit']
    list_filter = ['is_explicit', 'genres', 'artists']
    search_fields = ['title', 'artists__name', 'album__title']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['artists', 'genres']