from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

EVENTS_PATH = Path("app/data/system/analytics_events.jsonl")


def _read_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []

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

            events.append(event)

    return events


def _get_label(event: dict) -> str | None:
    label = event.get("data") or event.get("text")

    if not label:
        return None

    if isinstance(label, str) and label.startswith("/admin"):
        return None

    return str(label)


def get_recent_users(limit: int = 10) -> list[int]:
    events = _read_events()

    recent = []
    seen = set()

    for event in reversed(events):
        user_id = event.get("user_id")
        label = _get_label(event)

        if not user_id or not label:
            continue

        if user_id in seen:
            continue

        seen.add(user_id)
        recent.append(user_id)

        if len(recent) >= limit:
            break

    return recent


def build_recent_users_report(limit: int = 10) -> str:
    users = get_recent_users(limit=limit)

    if not users:
        return "👥 Пользователи\n\nНет действий пользователей"

    text = "👥 Последние активные пользователи\n\n"
    text += f"Показано: {len(users)}\n\n"

    for i, user_id in enumerate(users, start=1):
        text += f"{i}. 👤 {user_id}\n"

    text += "\nНажмите на пользователя, чтобы посмотреть его путь."

    return text


def build_user_flow_report(user_id: int | None = None, limit: int = 20) -> str:
    events = _read_events()

    clean_events = []

    for event in events:
        event_user_id = event.get("user_id")
        label = _get_label(event)

        if not event_user_id or not label:
            continue

        clean_events.append({
            "user_id": event_user_id,
            "type": event.get("type"),
            "label": label,
            "ts": event.get("ts"),
        })

    if not clean_events:
        return "Нет действий пользователей"

    target_user_id = user_id or clean_events[-1]["user_id"]

    user_events = [
        e for e in clean_events
        if e["user_id"] == target_user_id
    ][-limit:]

    if not user_events:
        return f"🧭 Путь пользователя\n\n👤 User ID: {target_user_id}\n\nДействий не найдено."

    text = "🧭 Путь пользователя\n\n"
    text += f"👤 User ID: {target_user_id}\n"
    text += f"👣 Последние шаги: {len(user_events)}\n\n"

    for e in user_events:
        text += f"→ {e['label']}\n"

    return text


def build_analytics_report() -> str:
    events = _read_events()

    if not events:
        return "Нет данных аналитики"

    users = set()
    actions = 0
    callbacks = Counter()
    last_events = []

    for event in events:
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
    events = _read_events()

    if not events:
        return "Нет данных аналитики"

    last_by_user = {}

    for event in events:
        user_id = event.get("user_id")
        label = _get_label(event)

        if not user_id or not label:
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