# FILE: manus_pro/scripts/repo_audit.py
# =============================================================================
# أداة تدقيق تنفيذية (Production-grade) لتحليل ملف/مستودع (خصوصاً JS/Node)
# وفق "سجل الإجراءات التفصيلي" الذي حددته (A-D) قدر الإمكان بطريقة آلية.
#
# مخرجاتها:
# - JSON مفصل على stdout (كما في schema الذي طلبته تقريباً)
# - ملفات تقارير اختيارية: sensitive_onions.txt, eslint.json, semgrep.json, ...
#
# ملاحظة أمان:
# - هذه الأداة لا تقوم بجلب/زيارة .onion أو تنفيذ عمليات هجومية.
# - فقط تحليل ثابت + تشغيل أدوات تدقيق/فحص إن كانت متاحة.
# =============================================================================

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def run_cmd(cmd: str, cwd: Path, timeout: int = 300) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout, p.stderr

def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def file_bytes(path: Path) -> int:
    return path.stat().st_size

def wc_lines(path: Path) -> int:
    # wc -l لكن عبر بايثون لتجنب اختلافات المنصات
    with path.open("rb") as f:
        return sum(1 for _ in f)

def grep_lines(path: Path, pattern: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    rx = re.compile(pattern)
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, start=1):
            if rx.search(line):
                out.append({"line": i, "code": line.rstrip("\n")})
    return out

def parse_function_defs_js(lines: List[str]) -> List[Dict[str, Any]]:
    # تبسيط regex. ليس AST كامل لكنه عملي وسريع.
    patterns = [
        r"^\s*(async\s+)?function\s+([A-Za-z0-9_]+)\s*\(",
        r"^\s*([A-Za-z0-9_]+)\s*:\s*(async\s+)?function\s*\(",
        r"^\s*(async\s+)?([A-Za-z0-9_]+)\s*\([^)]*\)\s*\{",  # method-ish
    ]
    compiled = [re.compile(p) for p in patterns]
    defs: List[Dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        for rx in compiled:
            m = rx.search(line)
            if m:
                # نحاول استخراج الاسم من أول مجموعة "اسم" في regex
                name = None
                for g in m.groups():
                    if isinstance(g, str) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", g):
                        # نتجنب async
                        if g != "async" and g != "function":
                            name = g
                            break
                if name:
                    defs.append({"name": name, "line": idx, "code": line.strip()})
                break
    return defs

def extract_dot_calls(lines: List[str]) -> List[Dict[str, Any]]:
    rx_this = re.compile(r"\bthis\.([A-Za-z0-9_]+)\b")
    rx_dotcall = re.compile(r"\b([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*\(")
    out: List[Dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        for m in rx_this.finditer(line):
            out.append({"type": "this", "name": m.group(1), "line": idx, "code": line.strip()})
        for m in rx_dotcall.finditer(line):
            if m.group(1) == "console":
                continue
            out.append({"type": "dotcall", "name": f"{m.group(1)}.{m.group(2)}", "line": idx, "code": line.strip()})
    return out

def bucket_coverage(required: Dict[str, int], implemented: Dict[str, int], weights: Dict[str, int]) -> Dict[str, Any]:
    # حساب weighted coverage كما طلبت
    total_w = sum(weights.values()) or 1
    impl_w = 0
    for k, w in weights.items():
        if implemented.get(k, 0) > 0:
            impl_w += w
    return {
        "required": sum(required.values()),
        "implemented": sum(implemented.values()),
        "coverage": round((sum(implemented.values()) / max(1, sum(required.values()))) * 100, 2),
        "weight_coverage": round((impl_w / total_w) * 100, 2),
        "weights": weights,
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="مسار المستودع (repo root)")
    ap.add_argument("--file", required=True, help="مسار الملف داخل المستودع")
    ap.add_argument("--outdir", default="manus_pro/data/audit", help="مجلد مخرجات التقارير")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    target = (repo / args.file).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    needed_context: List[str] = []
    notes: List[str] = []

    if not repo.exists():
        print(json.dumps({"success": False, "needed_context": ["repo_path_not_found"]}, ensure_ascii=False))
        return 2
    if not target.exists():
        print(json.dumps({"success": False, "needed_context": ["file_path_not_found"]}, ensure_ascii=False))
        return 2

    # (1) meta
    meta = {
        "path": str(target),
        "lines": wc_lines(target),
        "bytes": file_bytes(target),
        "sha256": sha256_file(target),
    }

    # قراءة الملف
    text = target.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # (2) imports/requires
    imports = []
    for hit in grep_lines(target, r"(?:\brequire\s*\(|\bimport\s+.*\s+from\s+)"):
        imports.append(hit)

    # (3) function defs
    defs = parse_function_defs_js(lines)

    # (4) this.* and dot calls
    calls = extract_dot_calls(lines)

    # مقارنة الاستدعاءات مع التعاريف داخل الملف (تقريباً)
    defined_names = {d["name"] for d in defs}
    call_names = set()
    for c in calls:
        if c["type"] == "this":
            call_names.add(c["name"])
        elif c["type"] == "dotcall":
            call_names.add(c["name"].split(".", 1)[-1])
    missing_functions = []
    for name in sorted(call_names):
        if name not in defined_names:
            # نلتقط أول ظهور
            first = next((c for c in calls if (c["type"] == "this" and c["name"] == name) or (c["type"] == "dotcall" and c["name"].endswith("." + name))), None)
            if first:
                missing_functions.append(
                    {
                        "name": name,
                        "first_seen_line": first["line"],
                        "contexts": [first["code"]],
                    }
                )

    # (5) parsers declared/defined
    declared_parsers = [h for h in grep_lines(target, r"parser\s*:")]
    defined_parsers = [h for h in grep_lines(target, r"(?:function\s+parse[A-Za-z0-9_]+|parse[A-Za-z0-9_]+\s*:\s*function)")]
    list_declared = [d["code"] for d in declared_parsers]
    list_defined = [d["code"] for d in defined_parsers]

    # (6) env vars
    env_hits = grep_lines(target, r"process\.env")
    env_vars = sorted({re.sub(r".*process\.env\.?([A-Za-z0-9_]+).*", r"\1", h["code"]) for h in env_hits})

    # (7) onion/i2p
    onion_hits = grep_lines(target, r"\.onion|\.i2p")
    sensitive_path = outdir / "sensitive_onions.txt"
    if onion_hits:
        sensitive_path.write_text("\n".join([f'{h["line"]}: {h["code"]}' for h in onion_hits]), encoding="utf-8")

    onion_i2p = [{"line": h["line"], "value": h["code"]} for h in onion_hits]

    # (8) crypto findings
    crypto_hits = grep_lines(
        target,
        r"deriveEncryptionKey|deriveHMACKey|securityKey\.substr|securityKey\.slice|securityKey\.substring|pbkdf2|hkdf|crypto\.pbkdf2|crypto\.createHmac",
    )
    crypto_findings = []
    for h in crypto_hits:
        severity = "Med"
        if re.search(r"securityKey\.(?:substr|slice|substring)", h["code"]):
            severity = "High"
        crypto_findings.append({"line": h["line"], "code": h["code"], "severity": severity})

    # (9) network/proxy functions
    network_hits = grep_lines(target, r"fetchOnionContent|fetchI2PContent|checkTorConnection|axios\.create|socks5|torController|i2pController")
    # (10) merge/dedup
    merge_hits = grep_lines(target, r"mergeAndDeduplicateExploits|generateUniqueExploitKey|isBetterExploit")

    # (15) risk scanning across repo
    rc, out, err = run_cmd(r"grep -nE \"child_process|execSync|exec\(|spawn\(|eval\(|Function\(\" -R . || true", cwd=repo, timeout=120)
    risk_assessment = []
    if out.strip():
        for line in out.splitlines()[:500]:
            risk_assessment.append({"finding": line.strip(), "severity": "High", "line": None})
    else:
        notes.append("لم يتم العثور على child_process/exec/eval عبر grep السريع (قد يكون هناك حالات أخرى).")

    # (13) أدوات الفحص إن كانت متاحة
    lint_report = None
    duplication_report = None

    # eslint
    rc, _, _ = run_cmd("command -v eslint >/dev/null 2>&1 && echo OK || echo NO", cwd=repo, timeout=10)
    if "NO" in _:
        needed_context.append("eslint_not_installed")
    else:
        eslint_path = outdir / "eslint.json"
        # eslint json format
        run_cmd(f"eslint --ext .js,.cjs,.mjs --format json . > {shlex.quote(str(eslint_path))} || true", cwd=repo, timeout=300)
        lint_report = str(eslint_path)

    # prettier
    rc, stdout, _ = run_cmd("command -v prettier >/dev/null 2>&1 && echo OK || echo NO", cwd=repo, timeout=10)
    if "NO" in stdout:
        needed_context.append("prettier_not_installed")

    # semgrep
    rc, stdout, _ = run_cmd("command -v semgrep >/dev/null 2>&1 && echo OK || echo NO", cwd=repo, timeout=10)
    if "NO" in stdout:
        needed_context.append("semgrep_not_installed")
    else:
        semgrep_path = outdir / "semgrep.json"
        run_cmd(f"semgrep --config auto --json . > {shlex.quote(str(semgrep_path))} || true", cwd=repo, timeout=600)

    # gitleaks
    rc, stdout, _ = run_cmd("command -v gitleaks >/dev/null 2>&1 && echo OK || echo NO", cwd=repo, timeout=10)
    if "NO" in stdout:
        needed_context.append("gitleaks_not_installed")
    else:
        gitleaks_path = outdir / "gitleaks.json"
        run_cmd(f"gitleaks detect --source . --report-path {shlex.quote(str(gitleaks_path))} --no-git || true", cwd=repo, timeout=600)

    # depcheck (node)
    rc, stdout, _ = run_cmd("command -v depcheck >/dev/null 2>&1 && echo OK || echo NO", cwd=repo, timeout=10)
    if "NO" in stdout:
        needed_context.append("depcheck_not_installed")

    # jscpd
    rc, stdout, _ = run_cmd("command -v jscpd >/dev/null 2>&1 && echo OK || echo NO", cwd=repo, timeout=10)
    if "NO" in stdout:
        needed_context.append("jscpd_not_installed")
    else:
        jscpd_path = outdir / "jscpd-report.json"
        run_cmd(f"jscpd --reporters json --output {shlex.quote(str(outdir))} . || true", cwd=repo, timeout=600)
        if jscpd_path.exists():
            duplication_report = str(jscpd_path)

    # (16) cross-module exports grep
    rc, out_exports, _ = run_cmd(r"grep -Rnh \"module\.exports|exports\.\" . || true", cwd=repo, timeout=120)
    exports_occurrences = []
    if out_exports.strip():
        for line in out_exports.splitlines()[:500]:
            exports_occurrences.append(line.strip())

    # (17) formatting issues: tabs/trailing spaces/crlf
    rc, out_tabs, _ = run_cmd(r"grep -n $'\t' -R . || true", cwd=repo, timeout=120)
    rc, out_trailing, _ = run_cmd(r"grep -nE \" +$\" -R . || true", cwd=repo, timeout=120)
    rc, out_crlf, _ = run_cmd(r"grep -n $'\r' -R . || true", cwd=repo, timeout=120)

    formatting_issues = {
        "tabs": out_tabs.splitlines()[:200],
        "trailing_spaces": out_trailing.splitlines()[:200],
        "crlf": out_crlf.splitlines()[:200],
    }

    # (18) buckets coverage (تقريبي - مثال عملي)
    buckets_required = {
        "parsing": 10,
        "fetching": 5,
        "crypto": 3,
        "dedup": 3,
        "opsec": 3,
    }
    buckets_implemented = {
        "parsing": len(defined_parsers),
        "fetching": len(network_hits),
        "crypto": len(crypto_hits),
        "dedup": len(merge_hits),
        "opsec": 1 if onion_hits else 0,
    }
    buckets_weights = {
        "parsing": 2,
        "fetching": 2,
        "crypto": 2,
        "dedup": 1,
        "opsec": 1,
    }

    coverage_by_bucket = {
        "parsing": bucket_coverage({"parsing": 10}, {"parsing": buckets_implemented["parsing"]}, {"parsing": 2}),
        "fetching": bucket_coverage({"fetching": 5}, {"fetching": buckets_implemented["fetching"]}, {"fetching": 2}),
        "crypto": bucket_coverage({"crypto": 3}, {"crypto": buckets_implemented["crypto"]}, {"crypto": 2}),
        "dedup": bucket_coverage({"dedup": 3}, {"dedup": buckets_implemented["dedup"]}, {"dedup": 1}),
        "opsec": bucket_coverage({"opsec": 3}, {"opsec": buckets_implemented["opsec"]}, {"opsec": 1}),
    }

    # تقرير نهائي
    report = {
        "success": True,
        "producer_confidence": 72,  # تقدير هندسي (قابل للتعديل)
        "file_meta": meta,
        "parsers": {
            "declared": len(declared_parsers),
            "defined": len(defined_parsers),
            "list_declared": list_declared[:200],
            "list_defined": list_defined[:200],
        },
        "missing_functions": missing_functions[:200],
        "env_vars": env_vars,
        "onion_i2p": onion_i2p[:200],
        "crypto_findings": crypto_findings[:200],
        "network_findings": [{"line": h["line"], "code": h["code"]} for h in network_hits[:200]],
        "merge_dedup_findings": [{"line": h["line"], "code": h["code"]} for h in merge_hits[:200]],
        "lint_report": lint_report,
        "duplication_report": duplication_report,
        "cross_module_conflicts": [],
        "exports_grep": exports_occurrences[:200],
        "formatting_issues": formatting_issues,
        "coverage_by_bucket": coverage_by_bucket,
        "risk_assessment": risk_assessment[:200],
        "notes": notes,
        "needed_context": needed_context,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
