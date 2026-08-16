"""Offline speech-to-text via faster-whisper."""

from __future__ import annotations

import numpy as np
from faster_whisper import WhisperModel

from ansux.config import settings

_model: WhisperModel | None = None


def load_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(
            settings.WHISPER_MODEL_SIZE, device="cpu", compute_type="int8"
        )
    return _model


def transcribe(audio: np.ndarray) -> str:
    model = load_model()
    float_audio = audio.flatten().astype(np.float32) / 32768.0
    segments, _info = model.transcribe(float_audio, language="en")
    return " ".join(segment.text for segment in segments).strip().lower()
