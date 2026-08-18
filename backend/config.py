"""Configuration — env vars with defaults."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── MiniMax API ──────────────────────────────────────────────
    MINIMAX_API_KEY: str = ""  # required for cloud mode
    MINIMAX_API_URL: str = ""  # required for cloud mode

    # ── SGLang-Omni ───────────────────────────────────────────────
    # Endpoint local SGLang-Omni (auto-détection si vide)
    SGLANG_OMNI_HOST: str = "127.0.0.1"
    SGLANG_OMNI_PORT: int = 8000

    # ── Server ──────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8643

    model_config = {"env_file": "../.env", "extra": "ignore"}


settings = Settings()
