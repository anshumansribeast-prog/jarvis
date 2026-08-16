"""Time-aware startup greetings."""

from __future__ import annotations

import datetime
import random

from ansux.config import settings


def startup_greeting() -> str:
    hour = datetime.datetime.now().hour
    name = settings.USER_NAME
    assistant = settings.ASSISTANT_NAME

    if 5 <= hour < 12:
        pool = [
            f"Good morning, {name}. {assistant} is online.",
            f"Morning, {name}. {assistant} systems are ready.",
            f"Good morning, {name}. {assistant} — your workspace is ready.",
        ]
    elif 12 <= hour < 17:
        pool = [
            f"Good afternoon, {name}. {assistant} is online.",
            f"Good afternoon, {name}. {assistant} systems are ready.",
            f"Afternoon, {name}. {assistant} is standing by. What are we working on?",
        ]
    elif 17 <= hour < 22:
        pool = [
            f"Good evening, {name}. {assistant} is online.",
            f"Good evening, {name}. {assistant} is standing by. What are we working on?",
            f"Evening, {name}. {assistant} systems are ready.",
        ]
    else:
        pool = [
            f"Hello, {name}. {assistant} is online.",
            f"Welcome back, {name}. {assistant} systems are ready.",
            f"Hi {name}. {assistant} is standing by.",
        ]
    return random.choice(pool)


def wake_acknowledgement() -> str:
    name = settings.USER_NAME
    pool = [
        f"Yes, {name}.",
        f"Listening, {name}.",
        "I'm here.",
        "Go ahead.",
    ]
    return random.choice(pool)
