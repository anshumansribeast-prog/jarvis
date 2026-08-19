import numpy as np

import jarvis


def test_is_speech_true_when_above_threshold():
    audio = np.full((100, 1), 200, dtype=np.int16)
    assert jarvis.is_speech(audio, threshold=150) is True


def test_is_speech_false_when_silence():
    audio = np.zeros((100, 1), dtype=np.int16)
    assert jarvis.is_speech(audio, threshold=150) is False
