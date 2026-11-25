# Voice engine

The local speech engine: Hugging Face [speech-to-speech](https://github.com/huggingface/speech-to-speech) 1.1.0 with
model profiles, personas, project-local model weights and guarded fixes, driven by the `voice-engine` CLI.
This page is the engine's operating reference. Installation is in the [root README](../../README.md#install), tests
in [TESTING.md](../../TESTING.md), and design in [docs/architecture.md](../../docs/architecture.md).

## Commands

```bash
uv run voice-engine serve        # Realtime server for the browser app: ws://127.0.0.1:8765/v1/realtime
uv run voice-engine run          # conversation in the terminal (microphone and speakers), no browser
uv run voice-engine talk         # terminal client for an already running `serve`
uv run voice-engine config       # print the rendered upstream configuration
```

`run`, `serve` and `config` take `--profile` (default `fast`; `VOICE_ENGINE_PROFILE` changes it for `run` and
`serve`) and `--persona` (default `assistant`, or `VOICE_ENGINE_PERSONA`). `talk --url` targets another server. `run --speakers` mutes the microphone while the assistant talks, for use without
headphones (no interruptions).

`run` waits until it logs "Ready — start speaking." (about 8 s); press Ctrl+C to stop. macOS asks for microphone
access the first time: allow it for your terminal app (System Settings → Privacy & Security → Microphone).

`scripts/setup.sh [fast|quality|all]` is idempotent. It runs `uv sync --frozen`, then downloads and verifies that
profile's models, then runs the unit tests.

## Models

All weights live in `<project>/models/` (override with `VOICE_ENGINE_MODELS_DIR`), as plain files organized by component:

```
models/
  vad/silero-vad/torch-home/…            Silero VAD (torch.hub layout, pinned commit)
  vad/smart-turn-v3.2/                   Smart Turn v3.2 ONNX
  stt/parakeet-tdt-0.6b-v3/
  llm/qwen3.5-4b-4bit/                   fast profile
  llm/qwen3.5-9b-4bit/                   quality profile
  tts/qwen3-tts-1.7b-customvoice-6bit/
  tts/qwen3-tts-1.7b-base-6bit/          optional: Voice Studio cloning
  tts/qwen3-tts-1.7b-voicedesign-6bit/   optional: Voice Studio "Describe"
  text/nltk-data/                        tokenizer data upstream needs
  .hf-home/                              deliberately empty Hugging Face home
```

`model-manifest.yaml` lists every model's repository, pinned commit, quantization, license, path, and the size and
SHA-256 of every file. At run time models load only by path, with Hugging Face offline mode on and an empty
Hugging Face home, so a missing model fails loudly instead of being downloaded or taken from another cache.

| Command | What it does |
|---|---|
| `voice-engine models list` | status, size, license and quantization of every model; which models each profile needs |
| `voice-engine models download --profile <p>` / `--ids <id>…` | fetch models at their pinned revisions (skips verified ones) |
| `voice-engine models verify --profile <p>` | sizes and SHA-256 of every file, then renders every persona and validates the configuration |
| `voice-engine models migrate --profile <p>` | copy models from a local Hugging Face cache instead of downloading (`--source`, default `~/.cache/voice-engine/huggingface`; copy-on-write, the cache is left untouched) |
| `voice-engine models lock` | maintainers: record file hashes after changing a model |

## Profiles

Profiles are upstream speech-to-speech YAML with one addition: values like `manifest:llm/qwen3.5-4b-4bit` refer
to manifest entries and are replaced with absolute paths at launch (written to the git-ignored `.generated/`).

| File | Contents |
|---|---|
| `profiles/base.yaml` | VAD and Smart Turn thresholds, STT, LLM, TTS, `chat_size`, Realtime origin policy, optional models |
| `profiles/fast.yaml` | Qwen3.5-4B 4-bit (**default**) |
| `profiles/quality.yaml` | Qwen3.5-9B 4-bit |

- **Add a profile:** add `profiles/<name>.yaml` overlaying `base.yaml`; any upstream setting can be changed.
- **Add a model:** add it to `model-manifest.yaml`, download it, run `voice-engine models lock`, and reference it as
  `manifest:<id>`.
- Switching profiles needs a restart.

## Personas

A persona defines the assistant: `personas/<id>.yaml` with `host` (its name), `voice` and `prompt`.

| Persona | Assistant | Voice | Use |
|---|---|---|---|
| `assistant` (default) | a general conversation partner | the Voice Studio default (`conversation-default`) | the browser app |
| `ren-test` | Ren, a fictional test persona | preset Aiden | tests: the spoken test lines address "Ren" |

The system prompt is always the persona's `prompt` followed by the engine instructions (`ENGINE_INSTRUCTIONS` in
`voice_engine/interruption.py`). A persona cannot remove them, a profile that sets `init_chat_prompt` is rejected,
and clients can only choose a persona by id. A persona's voice is a built-in preset or `conversation-default`,
never a saved Voice Studio voice.

## Voice Studio

| Method | How | Model |
|---|---|---|
| Built-in | the CustomVoice presets: Aiden, Ryan, Serena, Vivian, Sohee, Ono Anna | CustomVoice |
| Record / Upload | a 3–30 s reference of a consenting speaker, transcribed by Parakeet | Qwen3-TTS **Base** clones it live |
| Describe | VoiceDesign speaks a fixed passage in three voices matching a description; the chosen clip becomes the reference | **VoiceDesign** to create, then Base |

Base and VoiceDesign are optional (`voice_engine.optional` in `profiles/base.yaml`); without them the Voice panel shows
those methods as unavailable.

**Memory:**
- About 8 GB with presets only.
- About 11 GB once a custom voice has been used (Base stays loaded).
- Up to about 14 GB while VoiceDesign generates candidates (released afterwards).

A custom voice adds about 30 ms to the first audio of each reply.

**Storage** (`<project>/data/voices/`, override `VOICE_ENGINE_VOICES_DIR`; private and git-ignored):
- `<voice-id>/profile.json`: model and pinned revision, reference transcript, method, design description, owner
  consent, timestamps.
- `<voice-id>/reference.wav`: 24 kHz mono.
- `settings.json`: the Conversation default.

Writes are atomic, and a damaged voice is listed as unavailable. If the default voice is deleted, Conversation
falls back to Serena.

**API** (`voice_engine/voice_api.py`; same origin policy as the WebSocket):

| Endpoint | Purpose |
|---|---|
| `GET /v1/voices` | voices, Conversation default, capabilities, whether a session is live |
| `POST /v1/voices/preview` | speak text in a voice or design candidate (WAV) |
| `POST /v1/voices?name=&method=&consent=true` | create a voice from a WAV reference |
| `POST /v1/voices/design/candidates` | generate candidates from a description |
| `POST /v1/voices/design` | save a candidate |
| `PATCH` / `DELETE /v1/voices/{id}` | rename / delete |
| `PUT /v1/voices/default` | set the Conversation default |

Generation is refused with 409 while a conversation is connected or another generation runs, and the voice a
conversation speaks in cannot be deleted until it ends. Uploads over 15 MB are refused with 413.

## Settings

All optional; see [`.env.example`](.env.example): `VOICE_ENGINE_MODELS_DIR`, `VOICE_ENGINE_VOICES_DIR`,
`VOICE_ENGINE_PROFILE`, `VOICE_ENGINE_PERSONA` and `VOICE_ENGINE_ALLOWED_ORIGINS`.
`VOICE_ENGINE_ALLOW_UNTESTED_UPSTREAM=1` lets the engine start with a speech-to-speech version other than 1.1.0; the
patches' code checks still run.
