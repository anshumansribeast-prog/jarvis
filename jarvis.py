"""
Jarvis — a hands-free, wake-word voice assistant.

How it works, in four pieces:
  1. WAKE WORD — wait_for_wake_word()     always-on listening for "Jarvis"
  2. EARS      — record_chunk() + transcribe()  turn your mic into text
  3. BRAIN     — handle_command()         decides what you meant
  4. VOICE     — speak()                  talks back and does the thing

No keyboard needed. Jarvis listens in short chunks; anything too quiet
to be speech is skipped (cheap, and keeps us from burning API calls on
silence). Once "Jarvis" is heard, it greets you and records your
actual command as a separate, longer recording.
"""

import datetime
import os
import random
import subprocess
import webbrowser

import truststore
truststore.inject_into_ssl()  # trust the same certificates Windows does

import numpy as np
import requests
import sounddevice as sd
from faster_whisper import WhisperModel
from piper import PiperVoice

import app_controller
import file_controller
import memory_controller
import system_controller
import window_controller

WAKE_WORDS = ("jarvis",)
WAKE_CHUNK_SECONDS = 2.5   # how long each "are they saying the wake word" listen is
RECORD_SECONDS = 4         # how long we record once woken, for the actual command
SAMPLE_RATE = 16000
PIPER_VOICE_PATH = "voices/en_US-lessac-medium.onnx"
WHISPER_MODEL_SIZE = "base.en"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_SYSTEM_PROMPT = (
    "You are Jarvis, a knowledgeable voice assistant. Answer confidently "
    "and specifically from what you know, don't hedge or refuse unless "
    "truly unsafe. Your reply is read aloud, not displayed, so answer in "
    "2-3 short plain sentences with no markdown, lists, or asterisks."
)

# Mean absolute amplitude (int16 samples) below which a chunk is treated as
# silence and never sent to the speech API. Room tone / a quiet room tends
# to sit under 50; normal speech into a laptop mic runs into the hundreds.
# If Jarvis never wakes up, this is probably set too high for your mic —
# lower it. If it wakes up on every cough, raise it.
SILENCE_RMS_THRESHOLD = 150

SITES = {
    "semicolon": "https://semicolon-anshu.netlify.app",
    "cosmos": "https://cosmos-anshu.netlify.app",
    "music": "https://music.youtube.com",
}

# Local coding-project folders, opened in VS Code — distinct from SITES
# above, which opens the live deployed websites in a browser instead.
PROJECTS = {
    "semicolon": r"C:\Users\Anshu\semicolon",
    "astronomy site": r"C:\Users\Anshu\astronomy-site",
    "cosmos": r"C:\Users\Anshu\cosmos-v2",
    "jarvis": r"C:\Users\Anshu\jarvis",
}

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why do Java developers wear glasses? Because they don't see sharp.",
    "How many programmers does it take to change a light bulb? "
    "None, that's a hardware problem.",
]

print("Loading voice (Piper) and speech recognition (Whisper) models...")
piper_voice = PiperVoice.load(PIPER_VOICE_PATH)
whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

# Wikipedia's API rejects requests with no User-Agent (403, "please set a
# user-agent and respect our robot policy") — identify ourselves honestly.
WIKI_HEADERS = {"User-Agent": "Jarvis-VoiceAssistant/1.0 (personal project, github.com/anshumansribeast-prog)"}


def _device_opens(index, seconds=0.05, samplerate=SAMPLE_RATE):
    """Actually try to open a stream on this device — a device can look
    perfectly valid in sd.query_devices() (right name, input channels > 0)
    and still refuse to open."""
    try:
        sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1,
               dtype="int16", device=index)
        sd.wait()
        return True
    except Exception:
        return False


def pick_input_device():
    """Find a mic input device that actually opens.

    Used to hard-pick a device by name (the Windows sound mapper, or
    failing that the first non-loopback input). That stopped working on
    this laptop: the sound-mapper entry no longer exists in the device
    list at all, and the fallback it picked instead — the Realtek
    "Microphone Array" under Windows' WDM-KS backend — enumerates fine
    but PortAudio can't actually open a stream on it (fails at every
    channel/samplerate combination tried). Meanwhile letting PortAudio
    resolve its own default device works and captures real audio. So
    don't just trust the device list — test-open each candidate for
    real, preferring anything that isn't Stereo Mix (a loopback of
    speaker output, not the mic), and fall back to PortAudio's own
    default if nothing explicit opens.
    """
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

    return None  # nothing explicit worked — let PortAudio's own default try


INPUT_DEVICE = pick_input_device()


_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "do", "does", "did",
    "give", "me", "tell", "for", "of", "to", "good", "some", "please",
    "what", "who", "how", "why", "when", "where", "and", "in", "on",
    "at", "it", "you", "i", "about", "your", "my", "today", "today's",
}


def _looks_related(query, topic):
    """Guard against a search engine confidently returning something real
    but unrelated. Wikipedia's full-text search in particular almost never
    comes back empty — it'll happily hand back an article on a completely
    different subject rather than admit no match (asking for a study
    motivation quote once returned a Subhas Chandra Bose biography). True
    unless the topic shares no meaningful word with what was actually asked.
    """
    query_words = {w for w in query.lower().split() if len(w) > 2 and w not in _STOPWORDS}
    topic_words = set(topic.lower().replace("(", " ").replace(")", " ").split())
    return bool(query_words & topic_words)


def duckduckgo_answer(query):
    """Ask DuckDuckGo's free instant-answer API for a short summary. No API key needed.

    Good for named things (people, places, concepts) it has a curated
    abstract for; it has no real coverage for open questions like "how
    many moons does Jupiter have", which is what wikipedia_answer below
    is for.
    """
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=5,
        )
        data = resp.json()
    except requests.RequestException:
        return None

    text = data.get("AbstractText")
    heading = data.get("Heading")
    if text and heading and not _looks_related(query, heading):
        text = None
    if not text and data.get("RelatedTopics"):
        first = data["RelatedTopics"][0]
        if isinstance(first, dict):
            text = first.get("Text")
    return text or None


def wikipedia_answer(query):
    """Fall back to Wikipedia for the world-knowledge questions DuckDuckGo's
    instant-answer API doesn't cover. Also free, also no API key — two public
    REST calls: full-text search to resolve the query to a real article
    title, then the summary endpoint for that title's lead paragraph.

    Uses action=query&list=search (real full-text search over article
    content) rather than action=opensearch (title-prefix matching only) —
    opensearch finds nothing for a natural question like "how many moons
    does Jupiter have" because no article title starts with that phrase.
    """
    try:
        search = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 1,
                "format": "json",
            },
            headers=WIKI_HEADERS,
            timeout=5,
        )
        hits = search.json().get("query", {}).get("search", [])
        if not hits:
            return None
        title = hits[0]["title"]
        if not _looks_related(query, title):
            return None

        summary = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}",
            headers=WIKI_HEADERS,
            timeout=5,
        )
        data = summary.json()
    except (requests.RequestException, IndexError, ValueError):
        return None

    return data.get("extract") or None


def web_answer(query):
    """Try DuckDuckGo first (fast, curated); fall back to Wikipedia (broader
    coverage) so ordinary spoken questions have somewhere to land besides
    "I don't know that command yet"."""
    return duckduckgo_answer(query) or wikipedia_answer(query)


def ask_ollama(query):
    """Ask the local Ollama model running on this laptop — Jarvis's actual
    brain for anything the web lookups above don't cover. Runs fully
    offline once the model is pulled. Returns None (not an exception) if
    Ollama isn't running or errors, so callers fall back the same way a
    missed web lookup does.
    """
    facts = memory_controller.all_facts()
    system_prompt = OLLAMA_SYSTEM_PROMPT
    if facts:
        system_prompt += " Known facts about the user: " + "; ".join(
            f"their {k} is {v}" for k, v in facts.items()) + "."

    projects = memory_controller.project_facts()
    if projects:
        system_prompt += " Anshuman's coding projects, which you know about and can help him think through: " + " ".join(
            f"{name} - {desc}" for name, desc in projects.items())

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": query,
                "system": system_prompt,
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
    except (requests.RequestException, ValueError):
        return None
    return text or None


def speak(text):
    print(f"Jarvis: {text}")
    # Piper synthesizes one chunk per sentence — play each as it's ready
    # rather than waiting for the whole reply, so longer answers don't
    # have a dead pause up front before Jarvis starts talking.
    for chunk in piper_voice.synthesize(text):
        sd.play(chunk.audio_int16_array, samplerate=chunk.sample_rate)
        sd.wait()


def confirm(prompt):
    """Speak a yes/no prompt and immediately record one short reply,
    without needing the wake word again. Returns True only for a clearly
    affirmative reply — silence, an unclear reply, or "no" are all
    treated as "no". This exists specifically for irreversible actions
    (deleting a file), where staying safe by default matters more than
    saving the user a repeated "Jarvis".
    """
    speak(prompt)
    audio = record_chunk(RECORD_SECONDS)
    reply = transcribe(audio)
    if reply:
        print(f"You said: {reply}")
    return any(word in reply for word in ("yes", "yeah", "yep", "confirm", "do it", "go ahead"))


def answer_question(query):
    """Look up query and speak the answer. Returns True if an answer was
    found and spoken, False if the caller needs to decide a fallback —
    the point is Jarvis actually answers out loud first, browser search
    is a last resort, not the default."""
    query = query.strip()
    if not query:
        speak("What do you want to know?")
        return True

    # Web lookups first — near-instant and won't make things up. Ollama
    # only runs when those find nothing, since it's slower on this laptop's
    # CPU and, unlike a Wikipedia extract, can be confidently wrong.
    answer = web_answer(query) or ask_ollama(query)
    if not answer:
        return False

    # Keep spoken answers to a couple of sentences — a multi-paragraph
    # reply read aloud in full stops being useful.
    sentences = answer.replace("\n", " ").split(". ")
    speak(". ".join(sentences[:3]).rstrip(".") + ".")
    return True


def record_chunk(seconds, samplerate=SAMPLE_RATE):
    """Record `seconds` of audio from the mic and return it as an int16 array."""
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate,
                    channels=1, dtype="int16", device=INPUT_DEVICE)
    sd.wait()
    return audio


def is_speech(audio, threshold=SILENCE_RMS_THRESHOLD):
    """Cheap silence gate so we don't run Whisper over empty air."""
    return float(np.abs(audio).mean()) > threshold


def transcribe(audio):
    """Turn a recorded int16 chunk into lowercase text, or "" if nothing usable was heard.

    Runs fully offline — no network call, unlike the old Google recognizer.
    """
    float_audio = (audio.flatten().astype(np.float32) / 32768.0)
    segments, _info = whisper_model.transcribe(float_audio, language="en")
    text = " ".join(segment.text for segment in segments).strip()
    return text.lower()


def wait_for_wake_word():
    """Block until "Jarvis" is heard. Keeps listening in short chunks forever."""
    print("Listening for the wake word 'Jarvis'...")
    while True:
        audio = record_chunk(WAKE_CHUNK_SECONDS)
        if not is_speech(audio):
            continue
        text = transcribe(audio)
        if text:
            print(f"Heard: {text}")
        if any(word in text for word in WAKE_WORDS):
            return


def handle_command(text):
    """Returns False to stop the assistant, True to keep listening."""
    if not text:
        return True

    # Checked before the "open semicolon"/"open cosmos" website shortcuts
    # below, since e.g. "open semicolon project" contains "open semicolon"
    # and would otherwise open the live site instead of the local folder.
    if text.startswith("open ") and text.rstrip("?.").endswith(" project"):
        name = text[len("open "):-len(" project")].strip().rstrip("?.")
        path = PROJECTS.get(name)
        if path:
            speak(f"Opening the {name} project.")
            subprocess.Popen(["code", path], shell=True)
        else:
            speak(f"Sir, I don't have a project called {name}.")

    elif "open my projects" in text or "open all projects" in text:
        speak("Opening all your projects.")
        for path in PROJECTS.values():
            subprocess.Popen(["code", path], shell=True)

    # Personal facts Jarvis is told to remember, e.g. "remember my favorite
    # song is Perfect by Ed Sheeran" / later "what's my favorite song".
    # Checked before the general "what is"/"who is" Q&A block further
    # below, which would otherwise swallow "what is my X" as a web search.
    elif text.startswith("remember that my ") or text.startswith("remember my "):
        lead = "remember that my " if text.startswith("remember that my ") else "remember my "
        rest = text[len(lead):].strip().rstrip("?.")
        if " is " not in rest:
            speak("Tell me what to remember, like: remember my favorite song is Perfect by Ed Sheeran.")
        else:
            key, value = rest.split(" is ", 1)
            key, value = key.strip(), value.strip()
            memory_controller.remember(key, value)
            speak(f"Got it. I'll remember your {key} is {value}.")

    elif any(text.startswith(lead) for lead in
             ("what is my ", "what's my ", "whats my ", "who is my ", "what are my ")):
        for lead in ("what is my ", "what's my ", "whats my ", "who is my ", "what are my "):
            if text.startswith(lead):
                key = text[len(lead):].strip().rstrip("?.")
                break
        value = memory_controller.recall(key)
        if value:
            speak(f"Your {key} is {value}.")
        else:
            speak(f"I don't know your {key} yet. You can tell me: remember my {key} is ...")

    elif "open semicolon" in text:
        speak("Opening Semicolon.")
        webbrowser.open(SITES["semicolon"])

    elif "open cosmos" in text:
        speak("Opening Cosmos.")
        webbrowser.open(SITES["cosmos"])

    elif "time" in text:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"It's {now}.")

    # These structured commands (exact prefixes like "switch to ", "close ")
    # must be checked before the loose "notepad"/"vs code"/"brave" substring
    # matches below — otherwise something like "switch to notepad" gets
    # swallowed by the bare "notepad" in text check and just reopens
    # Notepad instead of switching to it.
    elif text.startswith("switch to "):
        app_name = text[len("switch to "):].strip()
        if window_controller.switch_to(app_name):
            speak(f"Switching to {app_name}.")
        else:
            speak(f"Sir, I couldn't find a window for {app_name}.")

    elif text.startswith("close "):
        app_name = text[len("close "):].strip()
        if app_controller.close_app(app_name):
            speak(f"Closing {app_name}.")
        else:
            speak(f"Sir, I couldn't find {app_name} in my app list.")

    elif any(text.startswith(lead) for lead in ("open ", "launch ", "start ")):
        # "Open" covers three different things — try each in order: a
        # registered app, then a known folder (Downloads etc.), then
        # search the filesystem for a matching file or folder.
        lead = text.split(" ", 1)[0] + " "
        target = text[len(lead):].strip()
        if app_controller.launch_app(target):
            speak(f"Opening {target}.")
        elif file_controller.open_known_folder(target):
            speak(f"Opening your {target} folder.")
        else:
            matches = file_controller.find(target)
            if matches:
                file_controller.open_path(matches[0])
                speak(f"Opening {target}.")
            else:
                speak(f"Sir, I couldn't find {target} anywhere.")

    elif "minimize" in text:
        window_controller.minimize_active_window()
        speak("Minimized.")

    elif "maximize" in text:
        window_controller.maximize_active_window()
        speak("Maximized.")

    elif "restore" in text:
        window_controller.restore_active_window()
        speak("Restored.")

    elif "show my desktop" in text or "show desktop" in text:
        window_controller.show_desktop()
        speak("Showing your desktop.")

    elif "screenshot" in text:
        system_controller.take_screenshot()
        speak("Screenshot saved.")

    elif "increase the volume" in text or "volume up" in text:
        system_controller.volume_up()
        speak("Volume up.")

    elif "decrease the volume" in text or "volume down" in text:
        system_controller.volume_down()
        speak("Volume down.")

    elif "mute" in text:
        system_controller.mute()
        speak("Toggled mute.")

    elif "lock" in text:
        speak("Locking your computer.")
        system_controller.lock()

    elif "sleep" in text and any(w in text for w in ("computer", "laptop", "pc")):
        speak("Putting your computer to sleep.")
        system_controller.sleep()

    elif "shut down" in text or "shutdown" in text:
        if confirm("Are you sure you want to shut down the computer?"):
            speak("Shutting down. Goodbye, sir.")
            system_controller.shutdown()
        else:
            speak("Shutdown cancelled.")

    elif "restart" in text and any(w in text for w in ("computer", "laptop", "pc", "system")):
        if confirm("Are you sure you want to restart the computer?"):
            speak("Restarting now.")
            system_controller.restart()
        else:
            speak("Restart cancelled.")

    elif "notepad" in text:
        speak("Opening Notepad.")
        subprocess.Popen(["notepad.exe"])

    elif "vs code" in text or "visual studio code" in text:
        speak("Opening VS Code.")
        try:
            subprocess.Popen("code", shell=True)
        except FileNotFoundError:
            speak("I couldn't find VS Code on this laptop.")

    elif "brave" in text:
        speak("Opening Brave.")
        subprocess.Popen([BRAVE_PATH])

    elif "music" in text or "play song" in text:
        speak("Playing music.")
        webbrowser.open(SITES["music"])

    elif any(lead in text for lead in ("who is", "what is", "look up", "how many",
                                        "how much", "how far", "how long", "how old",
                                        "why is", "why do", "why does", "when did",
                                        "when was", "where is")):
        query = text
        for lead in ("who is", "what is", "look up", "how many", "how much",
                     "how far", "how long", "how old", "why is", "why do",
                     "why does", "when did", "when was", "where is"):
            if lead in query:
                query = query.split(lead, 1)[1].strip()
                break
        found = answer_question(query)
        if query and not found:
            speak(f"I couldn't find an answer for that, so I'm opening a search for {query}.")
            webbrowser.open(f"https://www.google.com/search?q={query}")

    # File commands are checked before the generic "search" branch below,
    # since "search my computer for X" contains the word "search" and
    # would otherwise be swallowed by the Google-search handler.
    elif text.startswith("create a folder") or text.startswith("create folder"):
        name = text.split("called", 1)[1].strip() if "called" in text else ""
        if not name:
            speak("What should I call the folder?")
        else:
            file_controller.create_folder(name)
            speak(f"Created the folder {name} on your desktop.")

    elif text.startswith("create a file") or text.startswith("create file"):
        name = text.split("called", 1)[1].strip() if "called" in text else ""
        if not name:
            speak("What should I call the file?")
        else:
            file_controller.create_file(name)
            speak(f"Created the file {name} on your desktop.")

    elif text.startswith("find ") or text.startswith("search my computer for "):
        lead = "find " if text.startswith("find ") else "search my computer for "
        query = text[len(lead):].strip()
        if not query:
            speak("What should I look for?")
        else:
            matches = file_controller.find(query)
            if not matches:
                speak(f"Sir, I couldn't find anything called {query}.")
            elif len(matches) == 1:
                speak(f"I found {os.path.basename(matches[0])}.")
            else:
                speak(f"I found {len(matches)} matches. The closest is {os.path.basename(matches[0])}.")

    elif text.startswith("read "):
        target = text[len("read "):].strip()
        matches = file_controller.find(target)
        if not matches:
            speak(f"Sir, I couldn't find {target}.")
        else:
            try:
                content, truncated = file_controller.read_text_file(matches[0])
            except (UnicodeDecodeError, OSError):
                speak(f"Sorry sir, I couldn't read {target}.")
            else:
                if not content.strip():
                    speak(f"{target} is empty.")
                else:
                    speak(content + (" ...and more." if truncated else ""))

    elif text.startswith("rename ") and " to " in text:
        old_name, new_name = text[len("rename "):].split(" to ", 1)
        old_name, new_name = old_name.strip(), new_name.strip()
        matches = file_controller.find(old_name)
        if not matches:
            speak(f"Sir, I couldn't find {old_name}.")
        else:
            file_controller.rename(matches[0], new_name)
            speak(f"Renamed {old_name} to {new_name}.")

    elif text.startswith("move ") and " to " in text:
        target, dest = text[len("move "):].split(" to ", 1)
        target, dest = target.strip(), dest.strip()
        matches = file_controller.find(target)
        if not matches:
            speak(f"Sir, I couldn't find {target}.")
        else:
            new_path = file_controller.move(matches[0], dest)
            if new_path:
                speak(f"Moved {target} to your {dest} folder.")
            else:
                speak(f"Sir, I don't have a folder called {dest} set up.")

    elif text.startswith("delete "):
        target = text[len("delete "):].strip()
        matches = file_controller.find(target)
        if not matches:
            speak(f"Sir, I couldn't find {target}.")
        else:
            kind = "folder" if os.path.isdir(matches[0]) else "file"
            if confirm(f"That will permanently delete the {kind} {target}. Do you want me to continue?"):
                try:
                    file_controller.delete(matches[0])
                except OSError:
                    speak(f"Sorry sir, I couldn't delete {target}.")
                else:
                    speak(f"Deleted {target}.")
            else:
                speak("Okay, I won't delete it.")

    elif "search" in text:
        query = text.split("search", 1)[1]
        query = query.replace("for", "", 1).strip()
        if query:
            speak(f"Searching Google for {query}.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("What do you want me to search for?")

    elif "joke" in text:
        speak(random.choice(JOKES))

    elif any(word in text for word in ("stop", "exit", "goodbye")):
        speak("Goodbye, Anshuman.")
        return False

    else:
        # Not a known command — try answering it as a general knowledge
        # question before giving up, so ordinary spoken questions ("how
        # tall is Everest") work even without a "what is"/"how many" lead.
        if not answer_question(text):
            speak("I don't know that one, and I couldn't find an answer either.")

    return True


def main():
    speak("Jarvis online. Say the word Jarvis whenever you need me.")
    running = True
    while running:
        wait_for_wake_word()
        speak("Yes sir.")
        audio = record_chunk(RECORD_SECONDS)
        text = transcribe(audio)
        if text:
            print(f"You said: {text}")
        try:
            running = handle_command(text)
        except Exception as exc:
            print(f"Command failed: {exc}")
            speak("Sorry sir, I couldn't complete that command.")
            running = True


if __name__ == "__main__":
    main()
