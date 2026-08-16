"""Wake-word and optional clap detection."""

from __future__ import annotations

import numpy as np

from ansux.config import settings
from ansux.voice import audio, stt


def heard_wake_word(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in settings.WAKE_WORDS)


def wait_for_wake(on_status=None) -> None:
    print(f"Listening for wake phrase ({', '.join(settings.WAKE_WORDS)})...")
    while True:
        chunk = audio.record_chunk(settings.WAKE_CHUNK_SECONDS)
        if not audio.is_speech(chunk):
            continue
        text = stt.transcribe(chunk)
        if text:
            print(f"Heard: {text}")
        if heard_wake_word(text):
            return
        if settings.CLAP_WAKE_ENABLED and _detect_double_clap(chunk):
            print("Double clap detected.")
            return
        if on_status:
            on_status("listening")


def _detect_double_clap(chunk: np.ndarray) -> bool:
    """Experimental: detect two sharp transients in one chunk."""
    samples = chunk.flatten().astype(np.float32)
    if samples.size < 100:
        return False
    abs_s = np.abs(samples)
    threshold = max(float(abs_s.mean()) * 8, 800)
    peaks = abs_s > threshold
    if peaks.sum() < 2:
        return False
    indices = np.where(peaks)[0]
    if len(indices) < 2:
        return False
    gaps = np.diff(indices[:10])
    return bool((gaps > 200).any())
