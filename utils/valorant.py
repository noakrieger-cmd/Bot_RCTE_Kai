"""Données VALORANT statiques, maintenues à la main (aucun appel réseau).

À mettre à jour quand Riot ajoute un agent : il suffit de l'ajouter dans AGENTS.
Dernière mise à jour : novembre 2026 (30 agents, Hush incluse).
"""

from __future__ import annotations

AGENTS: tuple[str, ...] = tuple(
    sorted(
        (
            "Astra", "Breach", "Brimstone", "Chamber", "Clove", "Cypher", "Deadlock",
            "Fade", "Gekko", "Harbor", "Hush", "Iso", "Jett", "KAY/O", "Killjoy", "Miks",
            "Neon", "Omen", "Phoenix", "Raze", "Reyna", "Sage", "Skye", "Sova", "Tejo",
            "Veto", "Viper", "Vyse", "Waylay", "Yoru",
        ),
        key=str.casefold,
    )
)


def match_agent(name: str) -> str | None:
    """Retourne le nom canonique d'un agent (insensible à la casse) ou None."""
    wanted = name.strip().casefold()
    return next((agent for agent in AGENTS if agent.casefold() == wanted), None)
