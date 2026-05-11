from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

EVENTS_PATH = Path("app/data/system/analytics_events.jsonl")


def build_user_flow_report(limit: int = 20) -> str:
    if not EVENTS_PATH.exists():
        return "Нет данных аналитики"

    events = []

    with EVENTS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                event = json.loads(line)
            except Exception:
                continue

            user_id = event.get("user_id")
            if not user_id:
                continue

            label = event.get("data") or event.get("text")
            if not label:
                continue

            if isinstance(label, str) and label.startswith("/admin"):
                continue

            events.append({
                "user_id": user_id,
                "type": event.get("type"),
                "label": label,
                "ts": event.get("ts"),
            })

    if not events:
        return "Нет действий пользователей"

    last_user_id = events[-1]["user_id"]

    user_events = [
        e for e in events
        if e["user_id"] == last_user_id
    ][-limit:]

    text = "🧭 Путь пользователя\n\n"
    text += f"👤 User ID: {last_user_id}\n"
    text += f"👣 Последние шаги: {len(user_events)}\n\n"

    for e in user_events:
        text += f"→ {e['label']}\n"

    return text


def build_analytics_report() -> str:
    if not EVENTS_PATH.exists():
        return "Нет данных аналитики"

    users = set()
    actions = 0
    callbacks = Counter()
    last_events = []

    with EVENTS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                event = json.loads(line)
            except Exception:
                continue

            user_id = event.get("user_id")
            if user_id:
                users.add(user_id)

            actions += 1

            if event.get("type") == "callback":
                data = event.get("data")
                if data:
                    callbacks[data] += 1

            last_events.append(event)

    top = callbacks.most_common(5)
    last_events = last_events[-5:]

    text = "📊 Аналитика AliMind\n\n"
    text += f"👥 Пользователей: {len(users)}\n"
    text += f"👣 Действий: {actions}\n\n"

    text += "🔥 Топ кнопок:\n"
    if top:
        for name, count in top:
            text += f"{name} — {count}\n"
    else:
        text += "Пока нет нажатий\n"

    text += "\n🕒 Последние действия:\n"
    for e in last_events:
        text += f"{e.get('type')} → {e.get('data') or e.get('text')}\n"

    return text
def build_exit_points_report() -> str:
    if not EVENTS_PATH.exists():
        return "Нет данных аналитики"

    last_by_user = {}

    with EVENTS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                event = json.loads(line)
            except Exception:
                continue

            user_id = event.get("user_id")
            if not user_id:
                continue

            label = event.get("data") or event.get("text")
            if not label:
                continue

            if isinstance(label, str) and label.startswith("/admin"):
                continue

            last_by_user[user_id] = label

    if not last_by_user:
        return "Нет точек выхода"

    exits = Counter(last_by_user.values())

    text = "🚪 Точки выхода\n\n"
    text += f"👥 Пользователей в анализе: {len(last_by_user)}\n\n"

    text += "Где пользователь остановился последним:\n"
    for label, count in exits.most_common(10):
        text += f"→ {label} — {count}\n"

    return text