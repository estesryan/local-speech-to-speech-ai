"""Personas (`personas/<id>.yaml`): the assistant's name (`host`), prompt and voice.

The system prompt is always the persona prompt followed by `ENGINE_INSTRUCTIONS`, which the interruption fix
depends on, so a persona cannot remove them. Profiles may not set the prompt, and Realtime clients can only choose a
persona by id (patches/session_persona.py).

A persona's voice is a built-in preset (`preset-aiden`) or `conversation-default`, the voice the user chose in Voice
Studio. A persona cannot name a saved voice (a synthetic copy of someone's voice), and clients cannot pick a voice.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .interruption import ENGINE_INSTRUCTIONS
from .paths import PERSONAS_DIR
from .voices import CONVERSATION_DEFAULT, PRESET_ID, is_voice_id

DEFAULT_PERSONA = "assistant"
_FIELDS = {"host", "voice", "prompt"}


class PersonaError(ValueError):
    pass


@dataclass(frozen=True)
class Persona:
    id: str
    host: str
    voice: str
    prompt: str

    def system_prompt(self) -> str:
        return " ".join([self.prompt.strip(), ENGINE_INSTRUCTIONS])


def available_personas(directory: Path = PERSONAS_DIR) -> list[str]:
    return sorted(p.stem for p in directory.glob("*.yaml"))


def load_persona(name: str, directory: Path = PERSONAS_DIR) -> Persona:
    path = directory / f"{name}.yaml"
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name) or not path.exists():
        raise PersonaError(f"unknown persona {name!r}; available: {', '.join(available_personas(directory))}")
    data = yaml.safe_load(path.read_text()) or {}
    if set(data) != _FIELDS:
        raise PersonaError(f"{path.name}: expected the fields {sorted(_FIELDS)}, got {sorted(data)}")
    for key in ("host", "prompt"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise PersonaError(f"{path.name}: {key} must be a non-empty string")
    voice = str(data["voice"])
    if voice != CONVERSATION_DEFAULT and not (PRESET_ID.fullmatch(voice) and is_voice_id(voice)):
        raise PersonaError(f"{path.name}: voice must be a built-in preset (preset-<name>) or {CONVERSATION_DEFAULT}")
    return Persona(id=name, **data)
