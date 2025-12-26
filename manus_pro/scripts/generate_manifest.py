# FILE: manus_pro/scripts/generate_manifest.py
# =============================================================================
# توليد manifest.json في جذر المستودع حسب Schema المطلوب:
# { project_name, language, language_version, files:[{path,sha256,size_bytes}], ... }
#
# ملاحظة:
# - يتجاهل .git و .venv و node_modules و dist و manus_pro/data (أسرار/حالة).
# - الهدف: Manifest قابل للتدقيق والتتبع.
# =============================================================================

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "manifest.json"

EXCLUDES = {
    ".git",
    ".venv",
    "manus_pro/data",
    "manus_pro/frontend/node_modules",
    "manus_pro/frontend/dist",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def is_excluded(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    for ex in EXCLUDES:
        if rel == ex or rel.startswith(ex.rstrip("/") + "/"):
            return True
    return False

def main() -> int:
    files: List[Dict] = []
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        if is_excluded(rel):
            continue
        try:
            files.append(
                {
                    "path": rel,
                    "sha256": sha256_file(p),
                    "size_bytes": p.stat().st_size,
                }
            )
        except Exception:
            continue

    manifest = {
        "project_name": "OpenManus-ManusPro",
        "language": "other",
        "language_version": "python>=3.12 + node>=20",
        "files": sorted(files, key=lambda x: x["path"]),
        "build_command": "bash validation.sh",
        "run_command": "PYTHONPATH=manus_pro/backend/src python -m manus_pro_server",
        "tests_command": "PYTHONPATH=manus_pro/backend/src pytest -q",
        "docker_image": "openmanus-manus-pro:local",
        "port": 8000,
        "env_vars": [
            {"name": "MANUS_PRO_DB_PATH", "example": "manus_pro/data/state.sqlite3", "required": False},
            {"name": "MANUS_PRO_WORKSPACE_ROOT", "example": "workspace", "required": False},
            {"name": "CEREBRAS_BASE_URL", "example": "https://api.cerebras.ai/v1", "required": False}
        ],
        "ci_file": ".github/workflows/ci.yml",
        "security_checks": ["semgrep", "trivy", "snyk"],
        "expected_test_output": "pytest exit code 0",
        "needed_context": [],
        "producer_confidence": 78,
        "assumptions": [
            "وجود Python 3.12 في بيئة التشغيل",
            "وجود Node 20 في بيئة التشغيل",
            "تشغيل النظام داخل بيئة معزولة مثل Codespaces"
        ],
    }

    OUT_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[manifest] written: {OUT_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
