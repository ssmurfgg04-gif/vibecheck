import os
import re
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path

MAX_REPO_SIZE_MB = 50
SEMGREP_TIMEOUT = 90


def get_semgrep_cmd() -> str:
    venv_semgrep = os.path.join(os.path.dirname(sys.executable), "semgrep.exe")
    if os.path.isfile(venv_semgrep):
        return venv_semgrep
    return "semgrep"


def clone_repo(github_url: str, target_dir: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1", "--single-branch", github_url, target_dir],
            capture_output=True,
            text=True,
            timeout=35,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_repo_size(path: str) -> bool:
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total < MAX_REPO_SIZE_MB * 1024 * 1024


# -------------------------------------------------------------
# Dedicated "Vibe Coding Sins" Pattern Scanners
# Specifically targets Supabase, Next.js, and hardcoded AI keys
# -------------------------------------------------------------

SECRET_PATTERNS = [
    (
        r"(?:NEXT_PUBLIC_)?(?:SUPABASE_SERVICE_ROLE_KEY|SERVICE_ROLE_KEY)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{20,}['\"]",
        "LEAKED_SUPABASE_SERVICE_ROLE",
        "CRITICAL",
        "Leaked Supabase service_role key. This admin key bypasses all Row-Level Security, giving anyone full read/write/delete access to your entire database.",
        "Remove this key from frontend code immediately. Put it only in server-side environment variables without the NEXT_PUBLIC_ prefix.",
    ),
    (
        r"(?:sk-[a-zA-Z0-9]{32,}|sk-ant-[a-zA-Z0-9]{32,}|sk-proj-[a-zA-Z0-9_-]{40,})",
        "HARDCODED_AI_API_KEY",
        "CRITICAL",
        "Hardcoded OpenAI or Anthropic API Key exposed in code. Hackers crawl public repos to steal keys and run up thousands of dollars in token bills.",
        "Revoke this key immediately in your AI provider dashboard and move it to a private .env.local file.",
    ),
    (
        r"sk_live_[a-zA-Z0-9]{24,}",
        "HARDCODED_STRIPE_SECRET_KEY",
        "CRITICAL",
        "Live Stripe Secret Key hardcoded in your repository. Anyone can use this to access customer data or trigger unauthorized charges and refunds.",
        "Roll this key in the Stripe Dashboard and ensure it is only accessed in backend environment variables.",
    ),
    (
        r"auth\.role\(\)\s*=\s*['\"]authenticated['\"]",
        "PERMISSIVE_SUPABASE_RLS",
        "ERROR",
        "Dangerously permissive Supabase policy. Checking auth.role() = 'authenticated' allows ANY logged-in user to view or modify records belonging to other users.",
        "Update the RLS policy to check user ownership directly: USING (auth.uid() = user_id).",
    ),
    (
        r"supabase\.auth\.getSession\(\)",
        "INSECURE_SUPABASE_GET_SESSION",
        "WARNING",
        "Using supabase.auth.getSession() in server components or middleware. It reads from unverified local cookies and can be spoofed.",
        "Replace getSession() with supabase.auth.getUser() to validate the token against the Supabase Auth server.",
    ),
]


def scan_vibe_specific_flaws(repo_path: str) -> list:
    """Scans for patterns specifically rampant in AI-generated / Cursor / Next.js codebases."""
    findings = []
    supported_exts = {
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".sql",
        ".env",
        ".env.local",
        ".env.example",
        ".json",
        ".py",
    }

    for dirpath, dirnames, filenames in os.walk(repo_path):
        # Skip node_modules and .git
        dirnames[:] = [
            d
            for d in dirnames
            if d not in ("node_modules", ".git", ".next", "dist", "build")
        ]
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext not in supported_exts:
                continue

            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, repo_path)

            try:
                with open(
                    full_path, "r", encoding="utf-8", errors="ignore"
                ) as handle:
                    lines = handle.readlines()
            except Exception:
                continue

            # Check Next.js server actions without auth
            is_ts_js = ext in (".ts", ".tsx", ".js", ".jsx")
            has_use_server = False
            if is_ts_js:
                file_text = "".join(lines)
                if "'use server'" in file_text or '"use server"' in file_text:
                    has_use_server = True
                    # Check if getUser or auth is checked inside mutations
                    if not re.search(
                        r"(getUser|auth\(|getServerSession|currentUser)",
                        file_text,
                    ):
                        findings.append(
                            {
                                "severity": "ERROR",
                                "rule_id": "vibecheck.nextjs.unprotected-server-action",
                                "category": "Auth Bypass",
                                "message": (
                                    "Next.js Server Action declared without any user authorization check. "
                                    "Anyone can trigger this server mutation over HTTP without being logged in."
                                ),
                                "file": rel_path,
                                "line": 1,
                                "code": lines[0].strip() if lines else "",
                                "plain_english": "Your Next.js server action accepts commands from the internet without checking if the person is logged in. Anyone can trigger this endpoint directly.",
                                "fix": "Add an authentication check (e.g., const { data: { user } } = await supabase.auth.getUser()) before performing any changes.",
                                "cursor_prompt": f"In file `{rel_path}`, protect all Server Actions with an authentication check. Call `await supabase.auth.getUser()` and throw an unauthorized error if no authenticated user is found.",
                            }
                        )

            # Check regex patterns line by line
            for i, line in enumerate(lines, 1):
                for pattern, rule_id, severity, desc, fix in SECRET_PATTERNS:
                    if re.search(pattern, line):
                        # Redact actual key snippet for safety
                        matched_snippet = line.strip()
                        if len(matched_snippet) > 120:
                            matched_snippet = matched_snippet[:120] + "..."

                        cat = "Secret Leak" if "KEY" in rule_id else "Database Security"
                        findings.append(
                            {
                                "severity": severity,
                                "rule_id": f"vibecheck.{rule_id.lower()}",
                                "category": cat,
                                "message": desc,
                                "file": rel_path,
                                "line": i,
                                "code": matched_snippet,
                                "plain_english": desc,
                                "fix": fix,
                                "cursor_prompt": f"In `{rel_path}` at line {i}: {fix}. Rewrite this to securely use environment variables or proper ownership checks.",
                            }
                        )

    return findings


def run_semgrep(path: str) -> list:
    cmd_bin = get_semgrep_cmd()
    try:
        result = subprocess.run(
            [
                cmd_bin,
                "--config=p/owasp-top-ten",
                "--config=p/secrets",
                "--config=p/security-audit",
                "--json",
                "--timeout",
                str(SEMGREP_TIMEOUT),
                "--max-memory",
                "512",
                "--no-git-ignore",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=SEMGREP_TIMEOUT + 15,
        )
        if result.stdout:
            data = json.loads(result.stdout)
            return data.get("results", [])
    except Exception as e:
        print(f"Semgrep error: {e}")
        return []
    return []


def parse_semgrep_findings(raw: list, repo_path: str) -> list:
    findings = []
    seen = set()

    # Filter out noisy or irrelevant non-vibe findings (like Dockerfile user warnings)
    noise_rules = {
        "missing-user-entrypoint",
        "missing-user",
        "mutable-action-tag",
    }

    for f in raw:
        rule_id = f.get("check_id", "")
        if any(noise in rule_id for noise in noise_rules):
            continue

        key = (
            f"{rule_id}:"
            f"{f.get('path','')}:"
            f"{f.get('start',{}).get('line',0)}"
        )
        if key in seen:
            continue
        seen.add(key)

        severity = f.get("extra", {}).get("severity", "WARNING").upper()
        message = f.get("extra", {}).get("message", "")
        raw_path = f.get("path", "")
        rel_path = raw_path.replace(repo_path, "").lstrip("/\\")
        line = f.get("start", {}).get("line", 0)
        code_snippet = f.get("extra", {}).get("lines", "")

        findings.append(
            {
                "severity": severity,
                "rule_id": rule_id,
                "category": "Code Quality / Logic",
                "message": message,
                "file": rel_path,
                "line": line,
                "code": code_snippet.strip() if code_snippet else "",
                "plain_english": message,
                "fix": "Refactor this logic to validate input before processing.",
                "cursor_prompt": f"In file `{rel_path}` at line {line}, review and fix this vulnerability: {message}. Provide the clean, secure implementation.",
            }
        )

    return findings


def calculate_vibe_score(findings: list) -> tuple:
    """Calculates a safety score from 0 to 100 and a label."""
    score = 100
    for f in findings:
        sev = f.get("severity", "WARNING")
        if sev == "CRITICAL":
            score -= 30
        elif sev == "ERROR":
            score -= 15
        elif sev == "WARNING":
            score -= 5
    score = max(5, score)

    if score >= 90:
        label = "Safe to Ship 🚀"
        status_color = "#3fb950"
    elif score >= 65:
        label = "Needs Attention ⚠️"
        status_color = "#d29922"
    else:
        label = "High Risk / Do Not Deploy 🚨"
        status_color = "#f85149"

    return score, label, status_color


def scan_repo(github_url: str) -> dict:
    tmp_dir = tempfile.mkdtemp(prefix="vibecheck_")
    repo_path = os.path.join(tmp_dir, "repo")

    try:
        if not clone_repo(github_url, repo_path):
            raise ValueError(
                "Could not clone repository. Make sure it's a valid public GitHub repo."
            )

        if not check_repo_size(repo_path):
            raise ValueError(
                f"Repository exceeds {MAX_REPO_SIZE_MB}MB limit. Try a smaller repository."
            )

        # 1. Specialized Vibe Coding Patterns (Supabase, Next.js, AI keys)
        vibe_findings = scan_vibe_specific_flaws(repo_path)

        # 2. Semgrep OWASP & Secret scans
        semgrep_raw = run_semgrep(repo_path)
        semgrep_findings = parse_semgrep_findings(semgrep_raw, repo_path)

        all_findings = vibe_findings + semgrep_findings

        # Sort: CRITICAL -> ERROR -> WARNING -> INFO
        order = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}
        all_findings.sort(key=lambda x: order.get(x["severity"], 4))
        top_findings = all_findings[:15]

        score, label, color = calculate_vibe_score(top_findings)

        return {
            "score": score,
            "label": label,
            "color": color,
            "findings": top_findings,
        }

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
