from rest_framework import serializers
from .models import Artist, Album, Track, Genre

# ====================================================================================================
# серіалізатори дозволяють перетворювати складні типи даних (наприклад, об'єкти моделей) в прості типи даних (наприклад, словники), які можуть бути легко перетворені в JSON або інші формати для передачі через API
# вони також дозволяють виконувати валідацію даних при створенні або оновленні об'єктів

# приклад серіалізатора для моделі Genre:
# ====================================================================================================

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id',
            'name',
            'slug',
            'description',
        ]
        read_only_fields = ['slug']


# =========================
# виконавець (READ/WRITE)
# =========================

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = [
            'id',
            'name',
            'slug',
            'bio',
            'country',
            'image',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def validate_name(self, value): # приклад валідації поля name
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Ім'я виконавця занадто коротке"
            )
        return value


# ==================================
# серіалізатор для альбому (READ)

# 2 рівні API:
# - READ API (важкий, nested, красивий JSON)
# artist - вся інформація з альбомами та треками
# album - підтягуються треки та виконавець
# - WRITE API (легкий, ID-based)
# Separate read/write serializers потрібні, щоб відокремити формат даних для отримання
# (GET, складні nested-структури, кешування) від формату для запису (POST/PUT, прості ID та мінімальні поля з валідацією)
# це дає контроль над API, кращу продуктивність і безпечну валідацію без перевантаження клієнта зайвими структурами
# ==================================

class AlbumReadSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True) # вкладений серіалізатор для виконавця
    genres = GenreSerializer(many=True, read_only=True) # вкладений серіалізатор для жанрів (many=True, бо це багато-до-багатьох)

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'slug',
            'artist',
            'release_date',
            'cover',
            'genres',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


# ==================================
# серіалізатор для альбому (WRITE)
# ==================================

class AlbumWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'artist',
            'release_date',
            'cover',
            'genres',
        ]

    def validate(self, attrs): # приклад валідації на рівні всього об'єкта (наприклад, перевірка унікальності комбінації назви та виконавця)
        title = attrs.get('title')
        artist = attrs.get('artist')

        if title and artist:
            exists = Album.objects.filter(
                title=title,
                artist=artist
            ).exists()

            if exists:
                raise serializers.ValidationError(
                    "Такий альбом вже існує для цього виконавця"
                )

        return attrs


# =================================
# серіалізатор для треку (READ)
# =================================

class TrackReadSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True, read_only=True) # !!! вкладений серіалізатор для виконавців !!!
    album = AlbumReadSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            'id',
            'title',
            'slug',
            'artists',
            'album',
            'genres',
            'duration',
            'duration_display',
            'track_number',
            'disc_number',
            'file',
            'is_explicit',
            'lyrics',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_duration_display(self, obj):
        return obj.get_duration_display()


# ===================================
# серіалізатор для треку (WRITE)
# ===================================

class TrackWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = [
            'id',
            'title',
            'album',
            'artists',
            'genres',
            'duration',
            'track_number',
            'disc_number',
            'file',
            'is_explicit',
            'lyrics',
        ]

    def validate_duration(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Тривалість не може бути від’ємною"
            )
        return value

    def validate(self, attrs):
        title = attrs.get('title')
        album = attrs.get('album')

        if title and album:
            if Track.objects.filter(
                title=title,
                album=album
            ).exists():
                raise serializers.ValidationError(
                    "Такий трек вже існує в цьому альбомі"
                )

        return attrs