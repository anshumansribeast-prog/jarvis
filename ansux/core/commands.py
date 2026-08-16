"""Command routing — preserves Jarvis behavior and adds AnshuX capabilities."""

from __future__ import annotations

import datetime
import os
import platform
import random
import subprocess
from typing import Callable

from ansux.config import settings
from ansux.core import context, knowledge, memory, modes, planner
from ansux.tools import apps, browser, filesystem, projects, system, windows

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why do Java developers wear glasses? Because they don't see sharp.",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
]

QA_LEADS = (
    "who is", "what is", "look up", "how many", "how much", "how far",
    "how long", "how old", "why is", "why do", "why does", "when did",
    "when was", "where is",
)


class CommandHandler:
    def __init__(self, speak: Callable[[str], None], confirm: Callable[[str], bool]):
        self.speak = speak
        self.confirm = confirm
        self.ctx = context.get_context()

    def _say(self, text: str) -> None:
        self.speak(modes.format_reply(text))

    def answer_question(self, query: str) -> bool:
        query = query.strip()
        if not query:
            self._say("What do you want to know?")
            return True
        answer = knowledge.web_answer(query) or knowledge.ask_ollama(query)
        if not answer:
            return False
        sentences = answer.replace("\n", " ").split(". ")
        self._say(". ".join(sentences[:3]).rstrip(".") + ".")
        return True

    def execute_plan(self, project_name: str, project_path: str) -> None:
        steps = planner.plan_development_workflow(project_name, project_path)
        self._say(f"Understood. Preparing {project_name} for development.")
        for step in steps:
            self._say(step.description)
            if step.action == "open_folder":
                projects.open_project_folder(step.args["path"])
            elif step.action == "open_vscode":
                if not projects.open_project_in_vscode(step.args["path"]):
                    self._say("I couldn't open VS Code.")
            elif step.action == "run_dev_server":
                ok, msg = projects.start_dev_server(
                    step.args["path"], step.args["manager"], step.args["script"], self.confirm
                )
                self._say(msg if ok else f"I couldn't start the dev server. {msg}")
            elif step.action == "run_command":
                ok, msg = projects.run_command(step.args["path"], step.args["command"], self.confirm)
                self._say(msg)
            elif step.action == "inspect_project":
                info = projects.inspect_project(step.args["path"])
                if info.get("scripts"):
                    self._say(f"Available scripts: {', '.join(info['scripts'][:5])}.")
                else:
                    self._say("Project inspected.")

    def handle(self, text: str) -> bool:
        if not text:
            return True

        self.ctx.record(text)
        mode_reply = modes.handle_mode_command(text)
        if mode_reply:
            self._say(mode_reply)
            return True

        lowered = text.lower()

        # Broad development workflow requests
        if any(p in lowered for p in ("ready for development", "work on my", "get my website", "prepare")):
            resolved = planner.resolve_project(text, self.ctx.last_project)
            if resolved:
                name, path = resolved
                self.ctx.set_project(name)
                self.execute_plan(name, path)
                return True

        if text.startswith("open ") and text.rstrip("?.").endswith(" project"):
            name = text[len("open "):-len(" project")].strip().rstrip("?.")
            ref = self.ctx.resolve_project_reference(text) or name
            path = settings.PROJECTS.get(ref)
            if path:
                self.ctx.set_project(ref)
                self._say(f"Opening the {ref} project.")
                projects.open_project_in_vscode(path)
            else:
                self._say(f"I don't have a project called {name}.")

        elif "open my projects" in lowered or "open all projects" in lowered:
            self._say("Opening all your projects.")
            for path in settings.PROJECTS.values():
                projects.open_project_in_vscode(path)

        elif lowered.startswith("remember that my ") or lowered.startswith("remember my "):
            lead = "remember that my " if lowered.startswith("remember that my ") else "remember my "
            rest = text[len(lead):].strip().rstrip("?.")
            if " is " not in rest:
                self._say("Tell me what to remember, like: remember my favorite song is Perfect.")
            else:
                key, value = rest.split(" is ", 1)
                ok, msg = memory.remember(key.strip(), value.strip())
                self._say(msg)

        elif lowered.startswith("forget "):
            key = text[len("forget "):].strip().rstrip("?.")
            ok, msg = memory.forget(key)
            self._say(msg)

        elif "show me what you remember" in lowered or "what do you remember" in lowered:
            self._say(memory.summarize_memory())

        elif "clear memory" in lowered or "clear your memory" in lowered:
            if self.confirm("Anshu, this will clear your stored personal facts. Proceed?"):
                self._say(memory.clear_all())
            else:
                self._say("Memory clear cancelled.")

        elif any(lowered.startswith(lead) for lead in
                 ("what is my ", "what's my ", "whats my ", "who is my ", "what are my ")):
            for lead in ("what is my ", "what's my ", "whats my ", "who is my ", "what are my "):
                if lowered.startswith(lead):
                    key = text[len(lead):].strip().rstrip("?.")
                    break
            value = memory.recall(key)
            self._say(f"Your {key} is {value}." if value else f"I don't know your {key} yet.")

        elif "open semicolon" in lowered:
            self._say("Opening Semicolon.")
            browser.open_site("semicolon")

        elif "open cosmos" in lowered:
            self._say("Opening Cosmos.")
            browser.open_site("cosmos")

        elif "open backend" in lowered or "open the backend" in lowered:
            self._say("Opening the backend.")
            browser.open_site("backend")

        elif "youtube" in lowered:
            self._say("Opening YouTube.")
            browser.open_site("youtube")

        elif "github" in lowered:
            self._say("Opening GitHub.")
            browser.open_site("github")

        elif "claude code" in lowered:
            self._say("Opening Claude Code.")
            if platform.system() == "Windows":
                try:
                    subprocess.Popen(["wt.exe", "claude"])
                except FileNotFoundError:
                    self._say("I couldn't find Windows Terminal.")
            else:
                self._say("Claude Code launch is only configured for Windows.")

        elif "time" in lowered:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self._say(f"It's {now}.")

        elif lowered.startswith("switch to "):
            app_name = text[len("switch to "):].strip()
            if windows.switch_to(app_name):
                self.ctx.set_app(app_name)
                self._say(f"Switching to {app_name}.")
            else:
                self._say(f"I couldn't find a window for {app_name}.")

        elif lowered.startswith("close "):
            app_name = text[len("close "):].strip()
            if apps.close_app(app_name):
                self._say(f"Closing {app_name}.")
            else:
                self._say(f"I couldn't find {app_name} in my app list.")

        elif any(lowered.startswith(lead) for lead in ("open ", "launch ", "start ")):
            lead = text.split(" ", 1)[0].lower() + " "
            target = text[len(lead):].strip()
            if apps.launch_app(target):
                self.ctx.set_app(target)
                self._say(f"Opening {target}.")
            elif filesystem.open_known_folder(target):
                self._say(f"Opening your {target} folder.")
            else:
                matches = filesystem.find(target)
                if matches:
                    filesystem.open_path(matches[0])
                    self._say(f"Opening {target}.")
                else:
                    self._say(f"I couldn't find {target} anywhere.")

        elif "minimize" in lowered:
            windows.minimize_active_window()
            self._say("Minimized.")

        elif "maximize" in lowered:
            windows.maximize_active_window()
            self._say("Maximized.")

        elif "restore" in lowered:
            windows.restore_active_window()
            self._say("Restored.")

        elif "show my desktop" in lowered or "show desktop" in lowered:
            windows.show_desktop()
            self._say("Showing your desktop.")

        elif "screenshot" in lowered:
            path = system.take_screenshot()
            self._say("Screenshot saved." if path else "Screenshots require Windows.")

        elif "increase the volume" in lowered or "volume up" in lowered:
            system.volume_up()
            self._say("Volume up.")

        elif "decrease the volume" in lowered or "volume down" in lowered:
            system.volume_down()
            self._say("Volume down.")

        elif "mute" in lowered:
            system.mute()
            self._say("Toggled mute.")

        elif "lock" in lowered:
            self._say("Locking your computer.")
            system.lock()

        elif "sleep" in lowered and any(w in lowered for w in ("computer", "laptop", "pc")):
            self._say("Putting your computer to sleep.")
            system.sleep()

        elif "shut down" in lowered or "shutdown" in lowered:
            if self.confirm("Are you sure you want to shut down the computer?"):
                self._say(f"Shutting down. Goodbye, {settings.USER_NAME}.")
                system.shutdown()
            else:
                self._say("Shutdown cancelled.")

        elif "restart" in lowered and any(w in lowered for w in ("computer", "laptop", "pc", "system")):
            if self.confirm("Are you sure you want to restart the computer?"):
                self._say("Restarting now.")
                system.restart()
            else:
                self._say("Restart cancelled.")

        elif "notepad" in lowered:
            self._say("Opening Notepad.")
            if platform.system() == "Windows":
                subprocess.Popen(["notepad.exe"])

        elif "vs code" in lowered or "visual studio code" in lowered:
            self._say("Opening VS Code.")
            self.ctx.set_app("vs code")
            if not projects.open_project_in_vscode(os.getcwd()):
                self._say("I couldn't find VS Code.")

        elif "brave" in lowered:
            self._say("Opening Brave.")
            if platform.system() == "Windows":
                subprocess.Popen([settings.BRAVE_PATH])

        elif "music" in lowered or "play song" in lowered:
            self._say("Playing music.")
            browser.open_site("music")

        elif any(lead in lowered for lead in QA_LEADS):
            query = text
            for lead in QA_LEADS:
                if lead in lowered:
                    query = query.split(lead, 1)[1].strip()
                    break
            found = self.answer_question(query)
            if query and not found:
                self._say(f"I couldn't find an answer, so I'm opening a search for {query}.")
                browser.search_web(query)

        elif lowered.startswith("create a folder") or lowered.startswith("create folder"):
            name = text.split("called", 1)[1].strip() if "called" in text else ""
            if not name:
                self._say("What should I call the folder?")
            else:
                filesystem.create_folder(name)
                self._say(f"Created the folder {name} on your desktop.")

        elif lowered.startswith("create a file") or lowered.startswith("create file"):
            name = text.split("called", 1)[1].strip() if "called" in text else ""
            if not name:
                self._say("What should I call the file?")
            else:
                filesystem.create_file(name)
                self._say(f"Created the file {name} on your desktop.")

        elif lowered.startswith("find ") or lowered.startswith("search my computer for "):
            lead = "find " if lowered.startswith("find ") else "search my computer for "
            query = text[len(lead):].strip()
            if not query:
                self._say("What should I look for?")
            else:
                matches = filesystem.find(query)
                if not matches:
                    self._say(f"I couldn't find anything called {query}.")
                elif len(matches) == 1:
                    self._say(f"I found {os.path.basename(matches[0])}.")
                else:
                    self._say(f"I found {len(matches)} matches. The closest is {os.path.basename(matches[0])}.")

        elif lowered.startswith("read "):
            target = text[len("read "):].strip()
            matches = filesystem.find(target)
            if not matches:
                self._say(f"I couldn't find {target}.")
            else:
                try:
                    content, truncated = filesystem.read_text_file(matches[0])
                except (UnicodeDecodeError, OSError):
                    self._say(f"Sorry, I couldn't read {target}.")
                else:
                    if not content.strip():
                        self._say(f"{target} is empty.")
                    else:
                        self._say(content + (" ...and more." if truncated else ""))

        elif lowered.startswith("rename ") and " to " in lowered:
            old_name, new_name = text[len("rename "):].split(" to ", 1)
            matches = filesystem.find(old_name.strip())
            if not matches:
                self._say(f"I couldn't find {old_name.strip()}.")
            else:
                filesystem.rename(matches[0], new_name.strip())
                self._say(f"Renamed {old_name.strip()} to {new_name.strip()}.")

        elif lowered.startswith("move ") and " to " in lowered:
            target, dest = text[len("move "):].split(" to ", 1)
            matches = filesystem.find(target.strip())
            if not matches:
                self._say(f"I couldn't find {target.strip()}.")
            else:
                new_path = filesystem.move(matches[0], dest.strip())
                self._say(
                    f"Moved {target.strip()} to your {dest.strip()} folder."
                    if new_path else f"I don't have a folder called {dest.strip()}."
                )

        elif lowered.startswith("delete "):
            target = text[len("delete "):].strip()
            matches = filesystem.find(target)
            if not matches:
                self._say(f"I couldn't find {target}.")
            else:
                kind = "folder" if os.path.isdir(matches[0]) else "file"
                if self.confirm(f"That will permanently delete the {kind} {target}. Do you want me to continue?"):
                    try:
                        filesystem.delete(matches[0])
                        self._say(f"Deleted {target}.")
                    except OSError:
                        self._say(f"Sorry, I couldn't delete {target}.")
                else:
                    self._say("Okay, I won't delete it.")

        elif "search" in lowered:
            query = text.split("search", 1)[1].replace("for", "", 1).strip()
            if query:
                self._say(f"Searching Google for {query}.")
                browser.search_web(query)
            else:
                self._say("What do you want me to search for?")

        elif "joke" in lowered and modes.current_mode().value == "assistant":
            self._say(random.choice(JOKES))

        elif any(word in lowered for word in ("stop", "exit", "goodbye")):
            self._say(f"Goodbye, {settings.USER_NAME}.")
            return False

        else:
            if not self.answer_question(text):
                self._say("I don't know that one, and I couldn't find an answer either.")

        return True
