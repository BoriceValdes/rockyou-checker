"""
Vérifie que les deux copies du fichier de règles ANSSI (backend et
frontend) restent identiques.
La même analyse doit tourner à la fois côté backend
et côté navigateur, donc les paramètres des règles sont dupliqués
en JSON entre les deux services. Ce test transforme une divergence
silencieuse possible en échec de test explicite.
"""
from __future__ import annotations

import json
from pathlib import Path

_BACKEND_RULES = Path(__file__).parent.parent / "app" / "rules" / "anssi_rules.json"
_FRONTEND_RULES = Path(__file__).parent.parent.parent / "frontend" / "src" / "anssi-rules.json"


def test_anssi_rules_identical_between_backend_and_frontend():
    backend_rules = json.loads(_BACKEND_RULES.read_text(encoding="utf-8"))
    frontend_rules = json.loads(_FRONTEND_RULES.read_text(encoding="utf-8"))
    assert backend_rules == frontend_rules
