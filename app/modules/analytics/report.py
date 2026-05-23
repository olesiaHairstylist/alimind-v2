from __future__ import annotations

import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta, timezone

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
def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt
    except Exception:
        return None

def build_analytics_overview() -> str:
    events = _read_events()

    if not events:
        return "📊 Обзор системы\n\nНет данных аналитики."

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)

    all_users = set()
    active_24h = set()
    new_7d = set()
    first_seen: dict[int, datetime] = {}

    callbacks = Counter()
    today_actions = 0

    last_events = []

    for event in events:
        user_id = event.get("user_id")
        ts = _parse_ts(event.get("ts"))

        if user_id:
            all_users.add(user_id)

            if ts:
                if user_id not in first_seen or ts < first_seen[user_id]:
                    first_seen[user_id] = ts

                if ts >= day_ago:
                    active_24h.add(user_id)

        if ts and ts >= day_ago:
            today_actions += 1

        if event.get("type") == "callback":
            data = event.get("data")
            if data:
                callbacks[data] += 1

        label = _get_label(event)
        if label:
            last_events.append(label)

    for user_id, first_ts in first_seen.items():
        if first_ts >= week_ago:
            new_7d.add(user_id)

    top = callbacks.most_common(5)
    last_events = last_events[-5:]

    text = "📊 Обзор системы AliMind\n\n"

    text += "👥 Пользователи\n"
    text += f"Всего: {len(all_users)}\n"
    text += f"Активных за 24ч: {len(active_24h)}\n"
    text += f"Новых за 7 дней: {len(new_7d)}\n\n"

    text += "📈 Активность\n"
    text += f"Всего событий: {len(events)}\n"
    text += f"Действий за 24ч: {today_actions}\n\n"

    text += "🔥 Топ кнопок\n"
    if top:
        for data, count in top:
            text += f"→ {data} — {count}\n"
    else:
        text += "Пока нет нажатий\n"

    text += "\n🕒 Последние действия\n"
    if last_events:
        for label in last_events:
            text += f"→ {label}\n"
    else:
        text += "Нет действий\n"

    return text