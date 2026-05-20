# https://api.deezer.com/playlist/10423097922

import requests

from django.core.management.base import BaseCommand
from api.models import Artist, Album, Track


class Command(BaseCommand):
    help = "Завантаження даних із плейлиста Deezer (повністю безпечна версія)"

    def handle(self, *args, **kwargs):

        playlist_id = "10423097922"
        url = f"https://api.deezer.com/playlist/{playlist_id}"

        response = requests.get(url)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Помилка API"))
            return

        data = response.json()

        tracks = data.get("tracks", {}).get("data", [])

        total = len(tracks)
        self.stdout.write(f"Знайдено треків: {total}")

        success = 0
        failed = 0

        for i, item in enumerate(tracks, start=1):

            try:
                artist_name = item["artist"]["name"]
                album_title = item["album"]["title"]
                track_title = item["title"]
                duration = item.get("duration")

                artist, _ = Artist.objects.get_or_create(
                    name=artist_name,
                    defaults={"country": ""}
                )

                album, _ = Album.objects.get_or_create(
                    title=album_title,
                    artist=artist
                )

                track, created = Track.objects.get_or_create(
                    title=track_title,
                    album=album,
                    defaults={"duration": duration}
                )

                track.artists.add(artist)

                success += 1

                self.stdout.write(
                    f"[{i}/{total}] УСПІХ: {artist_name} - {track_title}"
                )

            except Exception as e:
                failed += 1
                self.stdout.write(self.style.WARNING(
                    f"[{i}/{total}] ПОМИЛКА: {str(e)}"
                ))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"ГОТОВО. Успішно: {success}, Помилок: {failed}"
        ))