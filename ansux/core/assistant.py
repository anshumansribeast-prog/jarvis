"""AnshuX assistant runtime."""

from __future__ import annotations

import os
import platform
import subprocess
import threading
import time

import truststore

truststore.inject_into_ssl()

from ansux.config import settings
from ansux.ui.urls import local_hud_url, public_hud_url
from ansux.core import bridge, commands, greetings, status
from ansux.core.context import get_context

_state: dict = {
    "listening": False,
    "processing": False,
    "last_command": "",
    "last_reply": "",
    "text_mode": True,
    "voice_mode": False,
    "awaiting_confirmation": None,
}

_running = True


def get_state() -> dict:
    return dict(_state)


class AnshuXAssistant:
    def __init__(self, voice_enabled: bool | None = None):
        self.ctx = get_context()
        self._voice_ready = False
        self._handler: commands.CommandHandler | None = None
        self._command_lock = threading.Lock()
        self._running = True
        if voice_enabled is None:
            voice_enabled = not settings.TEXT_ONLY_MODE
        self._voice_enabled = voice_enabled

    def _mic_available(self) -> bool:
        try:
            import sounddevice as sd

            devices = sd.query_devices()
            return any(d.get("max_input_channels", 0) > 0 for d in devices)
        except Exception:
            return False

    def _voice_files_present(self) -> bool:
        voice_path = settings.PIPER_VOICE_PATH
        if not os.path.isabs(voice_path):
            voice_path = os.path.join(settings.ROOT, voice_path)
        return os.path.isfile(voice_path)

    def _init_voice(self) -> None:
        if not self._voice_enabled:
            print("Running in text-only mode.")
            return
        if not self._voice_files_present():
            print(f"Voice model not found at {settings.PIPER_VOICE_PATH}")
            print("Text input still works in the HUD. Run install_ansux.bat to download voices.")
            self._voice_enabled = False
            return
        if not self._mic_available():
            print("No microphone detected — use the text box in the HUD.")
            self._voice_enabled = False
            return
        try:
            from ansux.voice import audio, stt, tts

            print("Loading voice models...")
            tts.load_voice()
            stt.load_model()
            self._voice_ready = True
            _state["voice_mode"] = True
        except Exception as exc:
            print(f"Voice setup failed ({exc}). Text input still works in the HUD.")
            self._voice_enabled = False

    def _is_yes(self, text: str) -> bool:
        lowered = text.lower()
        return any(w in lowered for w in ("yes", "yeah", "yep", "confirm", "do it", "go ahead"))

    def _confirm(self, prompt: str) -> bool:
        bridge.begin_confirmation(prompt)
        _state["awaiting_confirmation"] = prompt
        _state["last_reply"] = prompt
        self._output(prompt)

        if self._voice_enabled and self._voice_ready:
            try:
                from ansux.voice import audio, stt

                reply_audio = audio.record_chunk()
                reply = stt.transcribe(reply_audio)
                if reply:
                    print(f"You said: {reply}")
                    approved = self._is_yes(reply)
                    bridge.signal_confirmation(approved)
                    _state["awaiting_confirmation"] = None
                    return approved
            except Exception as exc:
                print(f"Voice confirmation failed: {exc}. Type yes or no in the text box.")

        approved = bridge.wait_for_confirmation(settings.TEXT_CONFIRM_TIMEOUT)
        _state["awaiting_confirmation"] = None
        return approved

    def _confirm_text(self, text: str) -> bool:
        return self._is_yes(text)

    def _output(self, text: str) -> None:
        _state["last_reply"] = text
        if self._voice_ready:
            from ansux.voice import tts

            tts.speak(text)
        else:
            print(f"{settings.ASSISTANT_NAME}: {text}")

    def _speak(self, text: str) -> None:
        _state["last_reply"] = text
        if self._voice_ready:
            from ansux.voice import tts

            tts.speak(text)
        else:
            print(f"{settings.ASSISTANT_NAME}: {text}")

    def _handle_text_command(self, text: str) -> str:
        with self._command_lock:
            _state["processing"] = True
            _state["last_command"] = text
            self.ctx.record(text)
            try:
                keep_running = self._handler.handle(text)
                self._running = keep_running
            except Exception as exc:
                print(f"Command failed: {exc}")
                self._speak("Sorry, I couldn't complete that command.")
            finally:
                _state["processing"] = False
            reply = _state.get("last_reply", "")
            if reply:
                history = self.ctx.history
                if history and "assistant" not in history[-1]:
                    history[-1]["assistant"] = reply
            return reply

    def _voice_loop(self) -> None:
        from ansux.voice import audio, stt, wake

        while self._running and self._voice_enabled and self._voice_ready:
            _state["listening"] = True
            _state["processing"] = False
            try:
                wake.wait_for_wake(on_status=lambda s: _state.update({"listening": True}))
            except Exception as exc:
                print(f"Wake listener error: {exc}")
                time.sleep(2)
                continue
            _state["listening"] = False
            _state["processing"] = True
            self._speak(greetings.wake_acknowledgement())
            try:
                cmd_audio = audio.record_chunk()
                text = stt.transcribe(cmd_audio)
            except Exception as exc:
                print(f"Recording error: {exc}")
                _state["processing"] = False
                continue
            if text:
                print(f"You said: {text}")
            self._handle_text_command(text)

    def _start_hud(self) -> None:
        from ansux.ui.server import start_hud_server

        threading.Thread(
            target=start_hud_server,
            kwargs={"get_state": self._hud_payload},
            daemon=True,
        ).start()

    def run(self, with_hud: bool | None = None) -> None:
        global _running
        _running = True

        self._handler = commands.CommandHandler(self._speak, self._confirm)
        bridge.register_handlers(self._handle_text_command, self._confirm_text)
        _state["text_mode"] = True

        use_hud = settings.HUD_ENABLED if with_hud is None else with_hud
        if use_hud:
            self._start_hud()
            self._wait_for_hud_ready()
            print(f"Dashboard ready: {local_hud_url()}")
            if settings.OPEN_HUD_ON_START:
                self._open_hud_browser()

        # Voice loads after HUD is already up — a voice failure won't block the website.
        self._init_voice()

        self._output(greetings.startup_greeting())

        if self._voice_enabled and self._voice_ready:
            threading.Thread(target=self._voice_loop, daemon=True).start()

        print(f"Type commands at {local_hud_url()}")
        while self._running:
            time.sleep(1)

    def stop(self) -> None:
        self._running = False

    def _hud_payload(self) -> dict:
        snap = status.snapshot(voice_ready=self._voice_ready)
        snap.update(_state)
        snap["history"] = self.ctx.recent_summary()
        snap["awaiting_confirmation"] = bridge.awaiting_confirmation()
        snap["publicUrl"] = settings.PUBLIC_URL
        snap["localUrl"] = local_hud_url()
        return snap

    def _wait_for_hud_ready(self, timeout: float = 20.0) -> None:
        import urllib.error
        import urllib.request

        url = f"http://127.0.0.1:{settings.HUD_PORT}/api/status"
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                urllib.request.urlopen(url, timeout=1)
                return
            except (urllib.error.URLError, OSError):
                time.sleep(0.3)
        print("WARNING: HUD did not respond in time. Check for errors above.")

    def _open_hud_browser(self) -> None:
        url = local_hud_url()
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
        except OSError as exc:
            print(f"Could not open browser. Open manually: {url} ({exc})")


def main(voice_enabled: bool | None = None) -> None:
    AnshuXAssistant(voice_enabled=voice_enabled).run()
