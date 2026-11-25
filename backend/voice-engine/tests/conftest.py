import pytest


@pytest.fixture(autouse=True)
def private_voices_dir(tmp_path_factory, monkeypatch):
    """Tests never read or write the user's saved voices (data/voices)."""
    directory = tmp_path_factory.mktemp("voices")
    monkeypatch.setenv("VOICE_ENGINE_VOICES_DIR", str(directory))
    return directory
