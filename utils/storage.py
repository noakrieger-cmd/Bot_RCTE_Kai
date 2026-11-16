"""Asynchronous, serialized JSON persistence for the bot."""

from __future__ import annotations

import asyncio
import copy
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

DATA_PATH = Path(__file__).resolve().parents[1] / "data.json"
_lock = asyncio.Lock()


def default_data() -> dict[str, Any]:
    return {
        "settings": {"welcome_channel": None, "stream_channel": None, "match_channel": None},
        "accounts": {},
        "premier": {
            "rank": "Non défini", "standing": "Non classé",
            "current_presence": {"presents": [], "absents": [], "substitutes": []},
            "current_compo": {"players": {}}, "history": [], "planning": [],
            "debriefs": [],
        },
        "predictions": {"active": None, "scores": {}},
    }


def _read() -> dict[str, Any]:
    if not DATA_PATH.exists():
        return default_data()
    with DATA_PATH.open("r", encoding="utf-8") as stream:
        loaded = json.load(stream)
    if not isinstance(loaded, dict):
        raise ValueError("La racine de data.json doit être un objet JSON.")
    return _merge_defaults(loaded, default_data())


def _merge_defaults(data: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    for key, default_value in defaults.items():
        if key not in data:
            data[key] = copy.deepcopy(default_value)
        elif isinstance(data[key], dict) and isinstance(default_value, dict):
            _merge_defaults(data[key], default_value)
    return data


def _write(data: dict[str, Any]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = DATA_PATH.with_suffix(".json.tmp")
    with temporary_path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary_path, DATA_PATH)


async def load_data() -> dict[str, Any]:
    async with _lock:
        return await asyncio.to_thread(_read)


@asynccontextmanager
async def edit_data() -> AsyncIterator[dict[str, Any]]:
    """Hold one lock across read/modify/write to prevent lost updates."""
    async with _lock:
        data = await asyncio.to_thread(_read)
        yield data
        await asyncio.to_thread(_write, data)


async def save_data(data: dict[str, Any]) -> None:
    async with _lock:
        await asyncio.to_thread(_write, data)
