import os
import random
import httpx
from fastapi import HTTPException

LASTFM_BASE = "https://ws.audioscrobbler.com/2.0/"

GENRE_TO_TAG = {
    "Rock": "rock",
    "Pop": "pop",
    "Hip-Hop": "hip-hop",
    "Jazz": "jazz",
    "Clásica": "classical",
    "Electrónica": "electronic",
    "Folk": "folk",
    "Reggae": "reggae",
    "Urbano": "urban",
    "Metal": "metal",
}

async def get_random_track(genre: str) -> dict:
    api_key = os.getenv("LASTFM_API_KEY")
    if not api_key:
        raise HTTPException(500, "Falta LASTFM_API_KEY en el servidor")

    tag = GENRE_TO_TAG.get(genre)
    if not tag:
        raise HTTPException(400, f"Género inválido: {genre}")

    base_params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "limit": 50,
        "api_key": api_key,
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=12) as client:
        # 1) primera página para saber totalPages
        r1 = await client.get(LASTFM_BASE, params={**base_params, "page": 1})
        r1.raise_for_status()
        first = r1.json()

        if "error" in first:
            raise HTTPException(502, f"Last.fm error {first.get('error')}: {first.get('message')}")

        attr = first.get("toptracks", {}).get("@attr", {})
        total_pages = int(attr.get("totalPages", 1) or 1)

        page = random.randint(1, min(total_pages, 20))

        # 2) pedir página random y elegir un track random
        r2 = await client.get(LASTFM_BASE, params={**base_params, "page": page})
        r2.raise_for_status()
        data = r2.json()

        if "error" in data:
            raise HTTPException(502, f"Last.fm error {data.get('error')}: {data.get('message')}")

    tracks = data.get("toptracks", {}).get("track", [])
    if not tracks:
        raise HTTPException(404, "No se encontraron tracks")

    t = random.choice(tracks)
    artist = t.get("artist", {})
    artist_name = artist.get("name") if isinstance(artist, dict) else str(artist)

    return {
        "name": t.get("name"),
        "artist": artist_name,
        "url": t.get("url"),
        "tag": tag,
    }
