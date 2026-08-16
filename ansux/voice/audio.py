"""Microphone capture utilities."""

from __future__ import annotations

import numpy as np
import sounddevice as sd

from ansux.config import settings


def _device_opens(index: int, seconds: float = 0.05) -> bool:
    try:
        sd.rec(
            int(seconds * settings.SAMPLE_RATE),
            samplerate=settings.SAMPLE_RATE,
            channels=1,
            dtype="int16",
            device=index,
        )
        sd.wait()
        return True
    except Exception:
        return False


def pick_input_device() -> int | None:
    try:
        devices = sd.query_devices()
    except Exception:
        return None

    inputs = [i for i, d in enumerate(devices) if d["max_input_channels"] > 0]
    preferred = [i for i in inputs if "stereo mix" not in devices[i]["name"].lower()]
    loopback = [i for i in inputs if i not in preferred]

    for i in preferred + loopback:
        if _device_opens(i):
            return i
    return None


INPUT_DEVICE = pick_input_device()


def record_chunk(seconds: float | None = None) -> np.ndarray:
    duration = seconds or settings.RECORD_SECONDS
    audio = sd.rec(
        int(duration * settings.SAMPLE_RATE),
        samplerate=settings.SAMPLE_RATE,
        channels=1,
        dtype="int16",
        device=INPUT_DEVICE,
    )
    sd.wait()
    return audio


def is_speech(audio: np.ndarray, threshold: int | None = None) -> bool:
    limit = threshold if threshold is not None else settings.SILENCE_RMS_THRESHOLD
    return float(np.abs(audio).mean()) > limit
