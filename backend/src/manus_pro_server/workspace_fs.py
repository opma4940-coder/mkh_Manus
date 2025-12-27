# FileSystem Tool (Sandboxed) لاستخدامه من Dashboard/Backend:
# - استعراض المجلدات
# - قراءة/كتابة ملفات
# - رفع ملفات
#
# مبدأ الأمان:
# - كل العمليات محصورة داخل WORKSPACE_ROOT فقط (لا خروج عبر .. أو symlinks).

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

from .config import WORKSPACE_ROOT

def _resolve_in_workspace(user_path: str) -> Path:
    """
    يحول path القادم من UI إلى مسار آمن داخل WORKSPACE_ROOT فقط.
    """
    p = (WORKSPACE_ROOT / user_path.lstrip("/")).resolve()
    if WORKSPACE_ROOT not in p.parents and p != WORKSPACE_ROOT:
        raise ValueError("محاولة وصول خارج الـ Workspace (مرفوض).")
    return p

def list_dir(user_path: str) -> Dict:
    p = _resolve_in_workspace(user_path)
    if not p.exists():
        raise FileNotFoundError("المسار غير موجود.")
    if not p.is_dir():
        raise NotADirectoryError("المسار ليس مجلداً.")
    items: List[Dict] = []
    for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        try:
            stat = child.stat()
        except Exception:
            continue
        items.append(
            {
                "name": child.name,
                "path": str(child.relative_to(WORKSPACE_ROOT)).replace("\\", "/"),
                "type": "dir" if child.is_dir() else "file",
                "size_bytes": int(stat.st_size),
                "mtime": int(stat.st_mtime),
            }
        )
    return {"path": str(p.relative_to(WORKSPACE_ROOT)).replace("\\", "/"), "items": items}

def read_file(user_path: str, max_bytes: int = 1_000_000) -> Dict:
    p = _resolve_in_workspace(user_path)
    if not p.exists():
        raise FileNotFoundError("الملف غير موجود.")
    if not p.is_file():
        raise IsADirectoryError("المسار ليس ملفاً.")
    data = p.read_bytes()
    if len(data) > max_bytes:
        raise ValueError("حجم الملف كبير جداً للعرض عبر الواجهة (ارفع الحد أو استخدم RAG).")
    # نفترض UTF-8 مع fallback
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1", errors="replace")
    return {
        "path": str(p.relative_to(WORKSPACE_ROOT)).replace("\\", "/"),
        "size_bytes": len(data),
        "content": text,
    }

def write_file(user_path: str, content: str, create_dirs: bool = True) -> Dict:
    p = _resolve_in_workspace(user_path)
    if create_dirs:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"path": str(p.relative_to(WORKSPACE_ROOT)).replace("\\", "/"), "ok": True}

def make_dir(user_path: str) -> Dict:
    p = _resolve_in_workspace(user_path)
    p.mkdir(parents=True, exist_ok=True)
    return {"path": str(p.relative_to(WORKSPACE_ROOT)).replace("\\", "/"), "ok": True}
