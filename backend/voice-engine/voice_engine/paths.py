"""Project locations and the offline runtime environment.

Models load by explicit path from the models root (`<project>/models`, or VOICE_ENGINE_MODELS_DIR). Offline mode is
on and HF_HOME is an empty directory, so a missing model fails instead of being fetched or found in another cache.
"""

from __future__ import annotations

import os
from pathlib import Path

VOICE_ENGINE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = VOICE_ENGINE_DIR.parents[1]
MANIFEST_PATH = VOICE_ENGINE_DIR / "model-manifest.yaml"
PROFILES_DIR = VOICE_ENGINE_DIR / "profiles"
PERSONAS_DIR = VOICE_ENGINE_DIR / "personas"
GENERATED_DIR = VOICE_ENGINE_DIR / ".generated"
# default source for `voice-engine models migrate` (a Hugging Face home: <dir>/hub/models--…)
MIGRATE_CACHE = Path.home() / ".cache" / "voice-engine" / "huggingface"


def voices_dir() -> Path:
    """User-created voices (private: recordings and conditioning data). Not versioned."""
    return Path(os.environ.get("VOICE_ENGINE_VOICES_DIR", PROJECT_ROOT / "data" / "voices")).expanduser().resolve()


def models_root() -> Path:
    return Path(os.environ.get("VOICE_ENGINE_MODELS_DIR", PROJECT_ROOT / "models")).expanduser().resolve()


def runtime_env(root: Path | None = None) -> dict[str, str]:
    root = root or models_root()
    return {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        # deliberately empty: nothing is loaded by Hub ID, and nothing may come from ~/.cache
        "HF_HOME": str(root / ".hf-home"),
        "TORCH_HOME": str(root / "vad" / "silero-vad" / "torch-home"),
        "NLTK_DATA": str(root / "text" / "nltk-data"),
    }


def apply_runtime_env(root: Path | None = None) -> dict[str, str]:
    env = runtime_env(root)
    Path(env["HF_HOME"]).mkdir(parents=True, exist_ok=True)
    os.environ.update(env)
    return env
