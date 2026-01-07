from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os, random, httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/lastfm/random")
async def random_lastfm(genre: str):
    api_key = os.getenv("LASTFM_API_KEY")
    if not api_key:
        raise HTTPException(500, "Falta LASTFM_API_KEY")

    tag = GENRE_TO_TAG.get(genre)
    if not tag:
        raise HTTPException(400, f"Género inválido: {genre}")

    params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "limit": 50,
        "page": 1,
        "api_key": api_key,
        "format": "json",
    }

    headers = {"User-Agent": "mi_api/1.0"}

    async with httpx.AsyncClient(timeout=12, headers=headers) as client:
        r = await client.get(LASTFM_BASE, params=params)
        r.raise_for_status()
        data = r.json()

    # 👇 soporta ambos formatos: {"toptracks": {...}} o {"tracks": {...}}
    root = data.get("toptracks") or data.get("tracks") or {}
    tracks = root.get("track") or []

    # a veces viene un solo track como dict
    if isinstance(tracks, dict):
        tracks = [tracks]

    if not tracks:
        raise HTTPException(502, f"Last.fm devolvió 0 tracks. Keys: {list(data.keys())}")

    t = random.choice(tracks)
    artist = t.get("artist", {})
    artist_name = artist.get("name") if isinstance(artist, dict) else str(artist)

    return {
        "name": t.get("name"),
        "artist": artist_name,
        "url": t.get("url"),
        "tag": tag,
    }
