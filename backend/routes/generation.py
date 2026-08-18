"""MiniMax-Music3 generation endpoint — /api/generate."""

import httpx
import io
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["generation"])

# ── Models ──────────────────────────────────────────────────────────


class GenerateRequest(BaseModel):
    """Requête de génération MiniMax-Music3."""

    lyrics: str = Field(
        default="",
        description="Paroles de la chanson (peut contenir [Verse], [Chorus]…)",
    )
    prompt: str = Field(
        default="",
        description="Description musicale (genre, BPM, instruments, vocal…)",
    )
    seed: int = Field(default=7, description="Seed pour la reproductibilité")
    max_new_tokens: int = Field(
        default=750, le=9000, description="Durée max (frames, ~32s par 25fps)"
    )
    stream: bool = Field(default=False, description="Streaming (non supporté encore)")
    instrument: bool = Field(
        default=False, description="Générer sans paroles (instrumental)"
    )


class GenerationResponse(BaseModel):
    """Réponse avec URL du fichier audio généré."""

    generation_id: str
    audio_url: str
    duration_seconds: float = 0.0
    lyrics: str = ""


class LyricsRequest(BaseModel):
    """Générer des paroles depuis un prompt."""

    prompt: str


class LyricsResponse(BaseModel):
    """Paroles générées."""

    lyrics: str


# ── Helpers ───────────────────────────────────────────────────────────


UPLOAD_DIR = Path(__file__).parent.parent.parent / "temp"
UPLOAD_DIR.mkdir(exist_ok=True)


def _is_cloud_configured() -> bool:
    return bool(settings.MINIMAX_API_KEY and settings.MINIMAX_API_URL)


async def _generate_cloud(req: GenerateRequest) -> bytes:
    """Génération via l'API cloud MiniMax (openai-compatible)."""
    async with httpx.AsyncClient(timeout=300) as client:
        payload = {
            "model": "MiniMax-Music3",
            "input": req.lyrics,
            "instructions": req.prompt,
            "response_format": "wav",
            "seed": req.seed,
            "max_new_tokens": req.max_new_tokens,
        }
        headers = {"Authorization": f"Bearer {settings.MINIMAX_API_KEY}"}
        resp = await client.post(f"{settings.MINIMAX_API_URL}/v1/audio/speech", json=payload, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"MiniMax API error: {resp.text}")
        return resp.content


async def _generate_local(req: GenerateRequest) -> bytes:
    """Génération via SGLang-Omni local."""
    url = f"http://{settings.SGLANG_OMNI_HOST}:{settings.SGLANG_OMNI_PORT}/v1/audio/speech"
    async with httpx.AsyncClient(timeout=300) as client:
        payload = {
            "model": "MiniMaxAI/MiniMax-Music3",
            "input": req.lyrics,
            "instructions": req.prompt,
            "response_format": "wav",
            "seed": req.seed,
            "max_new_tokens": req.max_new_tokens,
            "stream": False,
        }
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"SGLang error {resp.status_code}: {resp.text}")
        return resp.content


async def generate_music(req: GenerateRequest) -> bytes:
    """Génère la musique — cloud ou local, selon config."""
    try:
        if _is_cloud_configured():
            return await _generate_cloud(req)
        else:
            return await _generate_local(req)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Génération trop longue — timeout")
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Service indisponible — vérifier que SGLang-Omni ou l'API cloud est running",
        )


# ── Endpoints ─────────────────────────────────────────────────────────


@router.post("/generate", response_model=GenerationResponse)
async def generate(req: GenerateRequest):
    """Génère une chanson et retourne l'URL de téléchargement."""
    generation_id = str(uuid.uuid4())[:8]

    if req.instrument:
        req.lyrics = ""

    content = await generate_music(req)

    filepath = UPLOAD_DIR / f"{generation_id}.wav"
    filepath.write_bytes(content)
    audio_url = f"/static/audio/{generation_id}.wav"

    # Estimer la durée : ~9000 frames → 360s (9 min) max
    duration = (req.max_new_tokens or 750) / 25.0

    return GenerationResponse(
        generation_id=generation_id,
        audio_url=audio_url,
        duration_seconds=duration,
        lyrics=req.lyrics,
    )


@router.post("/lyrics")
async def generate_lyrics(req: LyricsRequest):
    """Génère des paroles à partir d'un prompt (placeholder — à connecter à un LLM)."""
    # Placeholder: retourne une structure de base
    lyrics = (
        "[Verse]\n"
        "Your prompt here will generate lyrics\n"
        "That match the mood and style\n\n"
        "[Chorus]\n"
        "The music swells and grows\n"
        "Through every verse it flows\n"
    )
    return LyricsResponse(lyrics=lyrics)


@router.get("/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "cloud": _is_cloud_configured(),
        "sglang-omni": f"{settings.SGLANG_OMNI_HOST}:{settings.SGLANG_OMNI_PORT}",
    }


@router.get("/history")
async def list_history():
    """Liste des générations récentes."""
    files = sorted(UPLOAD_DIR.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
    items = []
    for f in files[:50]:
        items.append({
            "id": f.stem,
            "filename": f.name,
            "url": f"/static/audio/{f.name}",
            "size_mb": round(f.stat().st_size / 1_048_576, 2),
            "created": f.stat().st_mtime,
        })
    return {"generations": items}
