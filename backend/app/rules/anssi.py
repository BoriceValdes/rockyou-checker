"""
Analyse de conformité ANSSI des mots de passe.
Les règles elles-mêmes (seuils, motifs, jeux de caractères) sont définies
une seule fois en données dans anssi_rules.json et interprétées ici. La
même analyse doit aussi tourner dans le navigateur.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_RULES_PATH = Path(__file__).parent / "anssi_rules.json"


class AnssiSeverity(str, Enum):
    OK = "ok"
    WEAK = "weak"
    CRITICAL = "critical"


@dataclass(frozen=True)
class AnssiRuleResult:
    code: str
    label: str
    passed: bool


@dataclass(frozen=True)
class AnssiAnalysis:
    """
    Résultat de l'analyse d'un mot de passe selon les recommandations de
    l'ANSSI.
    """

    score: int  # 0 à 100
    severity: AnssiSeverity
    rules: list[AnssiRuleResult]

    @property
    def is_compliant(self) -> bool:
        return all(r.passed for r in self.rules)


def _min_length(pwd: str, rule: dict[str, Any]) -> bool:
    return len(pwd) >= rule["value"]


def _has_lower(pwd: str, _rule: dict[str, Any]) -> bool:
    return any(c.islower() for c in pwd)


def _has_upper(pwd: str, _rule: dict[str, Any]) -> bool:
    return any(c.isupper() for c in pwd)


def _has_digit(pwd: str, _rule: dict[str, Any]) -> bool:
    return any(c.isdigit() for c in pwd)


def _has_any_char(pwd: str, rule: dict[str, Any]) -> bool:
    return any(c in rule["chars"] for c in pwd)


def _no_sequence(pwd: str, rule: dict[str, Any]) -> bool:
    lowered = pwd.lower()
    window = rule["window"]
    for pattern in rule["patterns"]:
        for i in range(len(pattern) - window + 1):
            if pattern[i : i + window] in lowered:
                return False
    return True


def _no_repeated_char(pwd: str, rule: dict[str, Any]) -> bool:
    max_run = rule["max_run"]
    run = 1
    for i in range(1, len(pwd)):
        run = run + 1 if pwd[i] == pwd[i - 1] else 1
        if run > max_run:
            return False
    return True


_CHECKS: dict[str, Callable[[str, dict[str, Any]], bool]] = {
    "min_length": _min_length,
    "has_lower": _has_lower,
    "has_upper": _has_upper,
    "has_digit": _has_digit,
    "has_any_char": _has_any_char,
    "no_sequence": _no_sequence,
    "no_repeated_char": _no_repeated_char,
}


class AnssiComplianceChecker:
    """Évalue un mot de passe selon les règles définies dans anssi_rules.json."""

    def __init__(self) -> None:   
        self._spec = json.loads(_RULES_PATH.read_text(encoding="utf-8"))

    def analyze(self, password: str) -> AnssiAnalysis:
        rules = self._spec["rules"]
        results = [
            AnssiRuleResult(r["code"], r["label"], _CHECKS[r["type"]](password, r))
            for r in rules
        ]
        passed_count = sum(1 for r in results if r.passed)
        score = round(100 * passed_count / len(rules))

        thresholds = self._spec["severity_thresholds"]
        if score >= thresholds["ok_score"]:
            severity = AnssiSeverity.OK
        elif score >= thresholds["weak_min_score"]:
            severity = AnssiSeverity.WEAK
        else:
            severity = AnssiSeverity.CRITICAL

        return AnssiAnalysis(score=score, severity=severity, rules=results)
