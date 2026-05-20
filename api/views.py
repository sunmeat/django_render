from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.core.cache import cache

from .models import Artist, Album, Track, Genre
from .serializers import (
    ArtistSerializer,
    AlbumReadSerializer,
    AlbumWriteSerializer,
    TrackReadSerializer,
    TrackWriteSerializer,
    GenreSerializer,
)

# =======================================
# НАЛАШТУВАННЯ КЕШУ
# =======================================
CACHE_TTL = 60 * 5  # 5 хвилин


# =======================================
# ДОПОМІЖНІ ФУНКЦІЇ (ВЕРСІОНУВАННЯ КЕШУ)
# =======================================

def get_version(key: str) -> int:
    """
    Отримання поточної версії кешу для конкретної моделі.
    Якщо версія ще не існує — ініціалізується з 1.
    """
    version = cache.get(key)
    if version is None:
        version = 1
        cache.set(key, version)
    return version


def bump_version(key: str) -> None:
    """
    Збільшення версії кешу на 1 — це інвалідує всі старі ключі
    для даної моделі без явного їх видалення.
    """
    version = get_version(key) + 1
    cache.set(key, version)


# =======================================
# БАЗОВИЙ VIEWSET (DRY-логіка кешування)
# =======================================

class BaseCachedViewSet(ModelViewSet):
    """
    Базовий ViewSet із кешуванням GET-запитів на рівні даних.

    Кешуються серіалізовані дані (dict/list), а не об'єкт Response,
    оскільки Response не гарантовано серіалізується коректно у Redis/Memcached.
    """

    # ключ версії кешу — перевизначається в кожному дочірньому ViewSet
    cache_version_key: str = None

    # права доступу за замовчуванням — можна перевизначити за потреби
    permission_classes = [AllowAny]

    def _get_cache_version(self) -> int:
        """Повертає поточну версію кешу для цієї моделі."""
        return get_version(self.cache_version_key)

    def _build_cache_key(self, request, suffix: str = "") -> str:
        """
        Будує унікальний ключ кешу на основі:
        - назви класу (модель)
        - поточної версії (для інвалідації)
        - повного шляху з query-параметрами
        - суфіксу (list / retrieve)
        """
        version = self._get_cache_version()
        return (
            f"{self.__class__.__name__}"
            f":v{version}"
            f":{request.get_full_path()}"
            f":{suffix}"
        )

    # КЕШ ДЛЯ LIST
    def list(self, request, *args, **kwargs):
        cache_key = self._build_cache_key(request, "list")

        cached_data = cache.get(cache_key)
        # порожній список [] це теж валідний результат
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        # кешуються дані (response.data), а не сам об'єкт Response
        cache.set(cache_key, response.data, CACHE_TTL)
        return response

    # КЕШ ДЛЯ RETRIEVE
    def retrieve(self, request, *args, **kwargs):
        cache_key = self._build_cache_key(request, "retrieve")

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TTL)
        return response

    # ===================================================
    # ІНВАЛІДАЦІЯ КЕШУ (тільки для поточної моделі)
    # ===================================================

    def perform_create(self, serializer):
        """Після створення"""
        serializer.save()
        bump_version(self.cache_version_key)

    def perform_update(self, serializer):
        """Після оновлення"""
        serializer.save()
        bump_version(self.cache_version_key)

    def perform_destroy(self, instance):
        """Після видалення"""
        instance.delete()
        bump_version(self.cache_version_key)


# =========================
# виконавець
# =========================

class ArtistViewSet(BaseCachedViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["country", "name"]

    # окрема версія кешу для артистів
    cache_version_key = "artist_cache_version"


# =========================
# альбом
# =========================

class AlbumViewSet(BaseCachedViewSet):
    # select_related і prefetch_related зменшують кількість SQL-запитів
    queryset = Album.objects.select_related("artist").prefetch_related("genres")

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AlbumReadSerializer
        return AlbumWriteSerializer

    cache_version_key = "album_cache_version"


# =========================
# трек
# =========================

class TrackViewSet(BaseCachedViewSet):
    queryset = Track.objects.select_related("album").prefetch_related("artists", "genres")

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TrackReadSerializer
        return TrackWriteSerializer

    cache_version_key = "track_cache_version"


# =========================
# жанр
# =========================

class GenreViewSet(BaseCachedViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    cache_version_key = "genre_cache_version"