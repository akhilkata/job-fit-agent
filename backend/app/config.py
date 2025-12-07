import json
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# BASE_DIR = backend/ directory
BASE_DIR = Path(__file__).resolve().parent.parent
# .env lives in backend/
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Settings:
    """
    Centralized configuration for the backend.
    Currently only loads the candidate profile from profile/profile.json.
    """

    def __init__(self) -> None:
        profile_path_env = os.getenv("PROFILE_PATH")

        # PROFILE_PATH is relative to repo root (job-agent/)
        if profile_path_env:
            self.profile_path = (BASE_DIR.parent / profile_path_env).resolve()
        else:
            self.profile_path = (BASE_DIR.parent / "profile" / "profile.json").resolve()

        self.profile = self._load_profile()

    def _load_profile(self) -> dict:
        if not self.profile_path.exists():
            raise FileNotFoundError(
                f"Profile file not found at {self.profile_path}. "
                f"Make sure profile/profile.json exists."
            )
        with self.profile_path.open("r", encoding="utf-8") as f:
            return json.load(f)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached settings instance to avoid re-loading profile and env on every call.
    """
    return Settings()