from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wikiblocks.workspace import Workspace

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    ws = Workspace(tmp_path)
    ws.ensure_dirs()
    return ws


@pytest.fixture
def demo_analysis(fixtures: Path) -> dict:
    return json.loads((fixtures / "analysis" / "demo-talk.json").read_text(encoding="utf-8"))
