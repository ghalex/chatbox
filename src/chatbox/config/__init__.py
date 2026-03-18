"""
Configuration package.

Exports `settings` as a convenience so callers can do:
`from chatbox.config import settings`.
"""

from .settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
