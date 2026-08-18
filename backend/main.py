"""MiniMax-Music3 — FastAPI server."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routes import generation
from .config import settings

# ── Logging ──────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Lifespan ─────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🎵 MiniMax-Music3 API starting — cloud=%s, sglang-omni=%s:%d",
                "yes" if generation._is_cloud_configured() else "no",
                settings.SGLANG_OMNI_HOST, settings.SGLANG_OMNI_PORT)
    yield
    logger.info("🎵 MiniMax-Music3 API stopped")

# ── App ──────────────────────────────────────────────────────────────


app = FastAPI(
    title="MiniMax-Music3",
    description="AI Music Generation — MiniMax-Music3 API",
    version="0.1.0",
    lifespan=lifespan,
)

# ── Routes ────────────────────────────────────────────────────────────

app.include_router(generation.router)


# ── Static Files ──────────────────────────────────────────────────────

STATIC_DIR = Path(__file__).parent.parent / "frontend"
STATIC_DIR.mkdir(exist_ok=True)

# Mount static assets (css, js, audio)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Serve audio files from temp directory (project root / temp/)
app.mount("/static/audio", StaticFiles(directory=str(Path(__file__).parent.parent / "temp")), name="audio")

# Serve index.html at root
@app.get("/")
async def root():
    index = STATIC_DIR / "index.html"
    return FileResponse(str(index))
