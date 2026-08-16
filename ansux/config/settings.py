"""Central configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

USER_NAME = os.getenv("ANSUX_USER_NAME", "Anshu")
ASSISTANT_NAME = os.getenv("ANSUX_ASSISTANT_NAME", "AnshuX")
PIPER_VOICE_PATH = os.getenv("ANSUX_PIPER_VOICE", "voices/en_US-lessac-medium.onnx")
WHISPER_MODEL_SIZE = os.getenv("ANSUX_WHISPER_MODEL", "base.en")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
BRAVE_PATH = os.getenv(
    "ANSUX_BRAVE_PATH",
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
)
HUD_PORT = int(os.getenv("ANSUX_HUD_PORT", "8765"))
HUD_ENABLED = os.getenv("ANSUX_HUD_ENABLED", "true").lower() in ("1", "true", "yes")
SILENCE_RMS_THRESHOLD = int(os.getenv("ANSUX_SILENCE_THRESHOLD", "150"))
WAKE_CHUNK_SECONDS = float(os.getenv("ANSUX_WAKE_CHUNK_SECONDS", "2.5"))
RECORD_SECONDS = float(os.getenv("ANSUX_RECORD_SECONDS", "4"))
SAMPLE_RATE = 16000
STARTUP_ENABLED = os.getenv("ANSUX_STARTUP_ENABLED", "false").lower() in ("1", "true", "yes")
CLAP_WAKE_ENABLED = os.getenv("ANSUX_CLAP_WAKE_ENABLED", "false").lower() in ("1", "true", "yes")

WAKE_WORDS = tuple(
    w.strip().lower()
    for w in os.getenv("ANSUX_WAKE_WORDS", "anshux,anshu x,jarvis").split(",")
    if w.strip()
)

SITES = {
    "semicolon": "https://semicolon.punah.pro",
    "cosmos": "https://cosmos.punah.pro",
    "backend": "https://cosmos.punah.pro/backend.html",
    "music": "https://music.youtube.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
}

PROJECTS = {
    "semicolon": os.getenv("ANSUX_PROJECT_SEMICOLON", r"C:\Users\Anshu\semicolon"),
    "astronomy site": os.getenv("ANSUX_PROJECT_ASTRONOMY", r"C:\Users\Anshu\astronomy-site"),
    "astronomy world": os.getenv("ANSUX_PROJECT_ASTRONOMY", r"C:\Users\Anshu\astronomy-site"),
    "cosmos": os.getenv("ANSUX_PROJECT_COSMOS", r"C:\Users\Anshu\cosmos-v2"),
    "jarvis": os.getenv("ANSUX_PROJECT_JARVIS", r"C:\Users\Anshu\jarvis"),
    "anshux": str(ROOT),
}

OLLAMA_SYSTEM_PROMPT = (
    f"You are {ASSISTANT_NAME}, a knowledgeable personal AI assistant for {USER_NAME}. "
    "Answer confidently and specifically from what you know. Your reply is read aloud, "
    "not displayed, so answer in 2-3 short plain sentences with no markdown, lists, or asterisks."
)

WIKI_HEADERS = {
    "User-Agent": "AnshuX-VoiceAssistant/1.0 (personal project, github.com/anshumansribeast-prog)"
}
