"""Minimal Riot Account API client used for validating Riot IDs."""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import quote

import aiohttp
from dotenv import load_dotenv

# Charge explicitement le .env situé à la racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

EUROPE_BASE_URL = "https://europe.api.riotgames.com"


@dataclass(slots=True)
class RiotAccount:
    puuid: str
    game_name: str
    tag_line: str


class RiotAPIError(Exception):
    """Raised when Riot API validation fails or is unavailable."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def get_api_key() -> str | None:
    return os.getenv("RIOT_API_KEY")



async def lookup_account(game_name: str, tag_line: str) -> RiotAccount:
    """Lookup an account by Riot ID. Confirms existence, not account ownership."""
    api_key = get_api_key()
    if not api_key:
        raise RiotAPIError("La clé RIOT_API_KEY est absente de la configuration.")

    url = (
        f"{EUROPE_BASE_URL}/riot/account/v1/accounts/by-riot-id/"
        f"{quote(game_name, safe='')}/{quote(tag_line, safe='')}"
    )
    timeout = aiohttp.ClientTimeout(total=10)
    headers = {"X-Riot-Token": api_key}

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    payload = await response.json()
                    return RiotAccount(
                        puuid=payload["puuid"],
                        game_name=payload.get("gameName", game_name),
                        tag_line=payload.get("tagLine", tag_line),
                    )
                if response.status == 404:
                    raise RiotAPIError("Ce Riot ID n'existe pas (ou n'est pas trouvé).", 404)
                if response.status == 401:
                    raise RiotAPIError("La clé Riot API est invalide ou expirée.", 401)
                if response.status == 403:
                    raise RiotAPIError("Riot refuse l'accès à cet endpoint (403).", 403)
                if response.status == 429:
                    raise RiotAPIError("Limite de requêtes Riot atteinte. Réessayez plus tard.", 429)
                raise RiotAPIError(f"Riot API a répondu avec le code HTTP {response.status}.", response.status)
    except aiohttp.ClientError as error:
        raise RiotAPIError("Impossible de contacter Riot API pour le moment.") from error
    except TimeoutError as error:
        raise RiotAPIError("Riot API n'a pas répondu dans le délai imparti.") from error
