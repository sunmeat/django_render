from django.db import models
from django.utils.text import slugify


def generate_unique_slug(model, value, slug_field="slug"):
    base_slug = slugify(value) or "item"
    slug = base_slug
    counter = 1
    while model.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class Artist(models.Model):
    name       = models.CharField(max_length=255, unique=True, verbose_name="Ім'я")
    slug       = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='Slug')
    bio        = models.TextField(blank=True, verbose_name='Біографія')
    country    = models.CharField(max_length=100, blank=True, verbose_name='Країна')
    image      = models.ImageField(upload_to='artists/', blank=True, null=True, verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        ordering = ['name']
        verbose_name = 'Виконавець'
        verbose_name_plural = 'Виконавці'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Artist, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name        = models.CharField(max_length=100, unique=True, verbose_name='Назва')
    slug        = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Опис')

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Genre, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Album(models.Model):
    title        = models.CharField(max_length=255, verbose_name='Назва')
    slug         = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='Slug')
    artist       = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums', verbose_name='Виконавець')
    release_date = models.DateField(blank=True, null=True, verbose_name='Дата виходу')
    cover        = models.ImageField(upload_to='album_covers/', blank=True, null=True, verbose_name='Обкладинка')
    genres       = models.ManyToManyField(Genre, related_name='albums', blank=True, verbose_name='Жанри')
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at   = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        ordering = ['-release_date', 'title']
        unique_together = ('title', 'artist')
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбоми'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Album, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"


class Track(models.Model):
    title        = models.CharField(max_length=255, verbose_name='Назва')
    slug         = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='Slug')
    album        = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks', null=True, blank=True, verbose_name='Альбом')
    artists      = models.ManyToManyField(Artist, related_name='tracks', verbose_name='Виконавці')
    genres       = models.ManyToManyField(Genre, related_name='tracks', blank=True, verbose_name='Жанри')
    duration     = models.PositiveIntegerField(null=True, blank=True, verbose_name='Тривалість (сек)', help_text='Тривалість у секундах')
    track_number = models.PositiveIntegerField(null=True, blank=True, verbose_name='Номер треку')
    disc_number  = models.PositiveIntegerField(default=1, null=True, blank=True, verbose_name='Номер диску')
    file         = models.FileField(upload_to='tracks/', blank=True, null=True, verbose_name='Аудіофайл', help_text='Аудіофайл (mp3, wav тощо)')
    is_explicit  = models.BooleanField(default=False, verbose_name='Ненормативний контент')
    lyrics       = models.TextField(blank=True, verbose_name='Текст пісні')
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated_at   = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    class Meta:
        ordering = ['album', 'disc_number', 'track_number', 'title']
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Track, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        artists = ", ".join(a.name for a in self.artists.all()[:3])
        return f"{self.title} — {artists}"

    def get_duration_display(self):
        if not self.duration:
            return None
        return f"{self.duration // 60}:{self.duration % 60:02d}"