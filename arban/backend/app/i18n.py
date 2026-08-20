"""
Localization module for ARBAN.

Provides translation utilities for Persian (fa) and English (en) languages.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

LOCALES_DIR = Path(__file__).parent / "locales"

DEFAULT_LANGUAGE = "fa"
SUPPORTED_LANGUAGES = ["fa", "en"]


class Localizer:
    """Translation utility class."""

    def __init__(self, language: str = DEFAULT_LANGUAGE):
        self.language = language
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all translation files for the current language."""
        lang_dir = LOCALES_DIR / self.language
        if not lang_dir.exists():
            lang_dir = LOCALES_DIR / DEFAULT_LANGUAGE

        for file_path in lang_dir.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                category = file_path.stem
                self._translations[category] = json.load(f)

    def get(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a translation by dot-notation key.

        Example:
            loc.get("common.dashboard")  # Returns "داشبورد" for fa
            loc.get("errors.provider_unavailable")  # Returns translated error
        """
        parts = key.split(".")
        value = self._translations

        try:
            for part in parts:
                value = value[part]
            return str(value)
        except (KeyError, TypeError):
            # Fallback to English
            if self.language != "en":
                en_loc = Localizer("en")
                try:
                    return en_loc.get(key, default or key)
                except Exception:
                    pass
            return default or key

    def t(self, key: str, **kwargs: Any) -> str:
        """
        Translate a key with optional format arguments.

        Example:
            loc.t("alerts.net_roi", roi=2.5)  # Returns "ROI خالص: 2.5%"
        """
        text = self.get(key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

    def set_language(self, language: str) -> None:
        """Change the current language."""
        if language in SUPPORTED_LANGUAGES:
            self.language = language
            self._translations = {}
            self._load_translations()

    @property
    def is_rtl(self) -> bool:
        """Check if current language is RTL."""
        return self.language == "fa"


# Global default localizer instance
_default_localizer: Optional[Localizer] = None


def get_localizer(language: Optional[str] = None) -> Localizer:
    """Get or create a localizer instance."""
    global _default_localizer
    if language:
        return Localizer(language)
    if _default_localizer is None:
        _default_localizer = Localizer(DEFAULT_LANGUAGE)
    return _default_localizer


def t(key: str, **kwargs: Any) -> str:
    """Convenience function for translations using default localizer."""
    return get_localizer().t(key, **kwargs)


def get(key: str, default: Optional[str] = None) -> str:
    """Convenience function for getting translations."""
    return get_localizer().get(key, default)
