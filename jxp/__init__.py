"""Compatibility package for local development.

This repository stores CLI/source code under ``src/jxp`` while keeping
``jxp/`` for Reflex app files. When running commands directly from the repo
root (without editable install), Python resolves this package first.

Extend ``jxp.__path__`` to include ``src/jxp`` so imports like
``jxp.cli.commands.commands`` work in local runs.
"""

from pathlib import Path

_SRC_JXP = Path(__file__).resolve().parents[1] / "src" / "jxp"
if _SRC_JXP.exists():
    __path__.append(str(_SRC_JXP))

# Keep metadata available for imports like: from jxp import __logo__
__version__ = "0.1.4.post6"
__logo__ = "🐈"
