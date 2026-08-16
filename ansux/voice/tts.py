"""Offline text-to-speech via Piper."""

from __future__ import annotations

import sounddevice as sd
from piper import PiperVoice

from ansux.config import settings

_voice: PiperVoice | None = None


def load_voice() -> PiperVoice:
    global _voice
    if _voice is None:
        _voice = PiperVoice.load(settings.PIPER_VOICE_PATH)
    return _voice


def speak(text: str, label: str | None = None) -> None:
    name = label or settings.ASSISTANT_NAME
    print(f"{name}: {text}")
    voice = load_voice()
    for chunk in voice.synthesize(text):
        sd.play(chunk.audio_int16_array, samplerate=chunk.sample_rate)
        sd.wait()
