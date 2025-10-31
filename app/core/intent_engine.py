import json
import os
import re
import logging
import unicodedata
from difflib import SequenceMatcher
from typing import Optional, Dict, Any, List

from app.core.config import settings

logger = logging.getLogger(__name__)

_INTENTS: Dict[str, Any] = {}
_INTENTS_PATH = os.path.join(os.path.dirname(__file__), "intents.json")


def load_intents(force: bool = False) -> None:
    """Load intents from the JSON registry file into memory."""
    global _INTENTS
    if _INTENTS and not force:
        return
    try:
        with open(_INTENTS_PATH, "r", encoding="utf-8") as f:
            _INTENTS = json.load(f)
            if not isinstance(_INTENTS, dict):
                raise ValueError("Invalid intents.json format: root must be an object")
    except FileNotFoundError:
        logger.warning("intents.json not found at %s; special intents disabled", _INTENTS_PATH)
        _INTENTS = {"intents": []}
    except Exception as e:
        logger.error("Failed to load intents.json: %s", e)
        _INTENTS = {"intents": []}


def _match(text: str, matcher: Dict[str, Any]) -> bool:
    t = _normalize(text or "")
    m = matcher or {}
    mtype = m.get("type", "includes")
    patterns: List[str] = m.get("patterns", [])
    if not t or not patterns:
        return False
    if mtype == "includes":
        return any(_normalize(p or "") in t for p in patterns)
    if mtype == "regex":
        return any(re.search(p, t, re.IGNORECASE) for p in patterns)
    if mtype == "fuzzy":
        threshold = float(m.get("threshold", 0.82))
        return any(_fuzzy_contains(t, _normalize(p or ""), threshold) for p in patterns)
    return False


def _normalize(s: str) -> str:
    """Lowercase, strip, collapse whitespace, remove accents and most punctuation, reduce long repeats."""
    s = s.lower().strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"(.)\1{2,}", r"\1\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _fuzzy_contains(text: str, pattern: str, threshold: float) -> bool:
    """
    Approximate substring match: checks if any window in text is similar to pattern above threshold.
    Uses token windows with size equal to pattern's token length ±1.
    """
    if not text or not pattern:
        return False
    # Quick path: direct include
    if pattern in text:
        return True
    t_tokens = text.split()
    p_tokens = pattern.split()
    if not t_tokens or not p_tokens:
        return False
    p_len = len(p_tokens)
    # Consider windows of size p_len-1 to p_len+1
    for win_size in {max(1, p_len - 1), p_len, p_len + 1}:
        if win_size > len(t_tokens):
            continue
        for i in range(0, len(t_tokens) - win_size + 1):
            window = " ".join(t_tokens[i:i + win_size])
            score = SequenceMatcher(None, window, pattern).ratio()
            if score >= threshold:
                return True
    return False


def resolve(message: str) -> Optional[Dict[str, Any]]:
    """Resolve message to an action dict from the intents registry."""
    if not _INTENTS:
        load_intents()
    intents = _INTENTS.get("intents", [])
    for intent in intents:
        if _match(message, intent.get("match", {})):
            return intent.get("action")
    return None


def render_template(template: str) -> str:
    """Render a simple template replacing {{VAR}} with settings values."""
    if not template:
        return ""
    rendered = template
    replacements = {
        "{{PANTAS_NAME}}": getattr(settings, "PANTAS_NAME", "PANTAS"),
        "{{PANTAS_DESCRIPTION}}": getattr(settings, "PANTAS_DESCRIPTION", ""),
        "{{WHATSAPP_LINK}}": getattr(settings, "WHATSAPP_LINK", "https://wa.me/15551420825"),
        "{{WHATSAPP_NUMBER}}": getattr(settings, "WHATSAPP_NUMBER", "+1 (555) 142-0825"),
    }
    for key, value in replacements.items():
        rendered = rendered.replace(key, str(value or ""))
    return rendered
