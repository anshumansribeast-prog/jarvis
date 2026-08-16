"""AnshuX assistant runtime."""

from __future__ import annotations

import platform
import subprocess
import threading
import time

import truststore

truststore.inject_into_ssl()

from ansux.config import settings
from ansux.core import commands, greetings, status
from ansux.core.context import get_context
from ansux.voice import audio, stt, tts, wake

_state: dict = {
    "listening": False,
    "processing": False,
    "last_command": "",
    "last_reply": "",
}


def get_state() -> dict:
    return dict(_state)


class AnshuXAssistant:
    def __init__(self):
        self.ctx = get_context()
        self._voice_ready = False
        self._handler: commands.CommandHandler | None = None

    def _init_voice(self) -> None:
        print("Loading voice models...")
        tts.load_voice()
        stt.load_model()
        self._voice_ready = True

    def _confirm(self, prompt: str) -> bool:
        tts.speak(prompt)
        reply_audio = audio.record_chunk()
        reply = stt.transcribe(reply_audio)
        if reply:
            print(f"You said: {reply}")
        return any(w in reply for w in ("yes", "yeah", "yep", "confirm", "do it", "go ahead"))

    def _speak(self, text: str) -> None:
        _state["last_reply"] = text
        tts.speak(text)

    def run(self, with_hud: bool | None = None) -> None:
        self._init_voice()
        self._handler = commands.CommandHandler(self._speak, self._confirm)

        use_hud = settings.HUD_ENABLED if with_hud is None else with_hud
        if use_hud:
            from ansux.ui.server import start_hud_server

            threading.Thread(target=start_hud_server, kwargs={"get_state": self._hud_payload}, daemon=True).start()
            if settings.OPEN_HUD_ON_START:
                self._open_hud_browser()
                time.sleep(0.8)

        self._speak(greetings.startup_greeting())
        running = True
        while running:
            _state["listening"] = True
            _state["processing"] = False
            wake.wait_for_wake(on_status=lambda s: _state.update({"listening": True}))
            _state["listening"] = False
            _state["processing"] = True
            self._speak(greetings.wake_acknowledgement())
            cmd_audio = audio.record_chunk()
            text = stt.transcribe(cmd_audio)
            if text:
                print(f"You said: {text}")
                _state["last_command"] = text
            try:
                running = self._handler.handle(text)
            except Exception as exc:
                print(f"Command failed: {exc}")
                self._speak("Sorry, I couldn't complete that command.")
                running = True
            finally:
                _state["processing"] = False

    def _hud_payload(self) -> dict:
        snap = status.snapshot(voice_ready=self._voice_ready)
        snap.update(_state)
        snap["history"] = self.ctx.recent_summary()
        return snap

    def _open_hud_browser(self) -> None:
        url = f"http://127.0.0.1:{settings.HUD_PORT}"
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
        except OSError as exc:
            print(f"Could not open HUD browser: {exc}")


def main() -> None:
    AnshuXAssistant().run()
