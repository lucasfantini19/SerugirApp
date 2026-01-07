from fastapi import APIRouter
from app.services.lastfm import get_random_track

router = APIRouter()

@router.get("/random")
async def random_lastfm(genre: str):
    return await get_random_track(genre)
