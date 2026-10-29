import os
import json
import asyncio
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def _build_prompt(findings: list) -> str:
    lines = []
    for i, f in enumerate(findings, 1):
        lines.append(
            f"Finding #{i}:\n"
            f"  Rule: {f['rule_id']}\n"
            f"  Severity: {f['severity']}\n"
            f"  File: {f['file']} (line {f['line']})\n"
            f"  Message: {f['message']}\n"
            f"  Code: {f.get('code', 'N/A')}\n"
        )

    findings_block = "\n".join(lines)

    return f"""You are an elite security auditor translating code flaws for a vibe-coder (someone who built their Next.js/Supabase/AI app with Cursor/Claude and does not know low-level security jargon).

For each finding, provide:
1. "plain_english": Exactly 1-2 punchy sentences in plain English explaining what a hacker could do (e.g. steal all user emails, drain API credits, wipe the database).
2. "cursor_prompt": A direct instruction the founder can copy and paste into Cursor or Claude Code to make the AI assistant fix the code immediately. Be specific with filenames and functions.

Return ONLY a valid JSON array matching this exact schema:
[
  {{
    "id": 1,
    "plain_english": "...",
    "cursor_prompt": "..."
  }}
]

Findings:
{findings_block}"""


def _call_gemini(prompt: str) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text


async def summarize_findings(findings: list) -> list:
    """Enrich findings with plain-English summaries and direct Cursor fix prompts."""
    if not findings:
        return findings

    if not GEMINI_API_KEY:
        for f in findings:
            if not f.get("plain_english"):
                f["plain_english"] = f["message"]
            if not f.get("cursor_prompt"):
                f["cursor_prompt"] = (
                    f"In file `{f['file']}` around line {f['line']}, fix this security issue: {f['message']}. "
                    "Write secure code and preserve all existing functionality."
                )
        return findings

    prompt = _build_prompt(findings)

    try:
        text = await asyncio.to_thread(_call_gemini, prompt)
        text = text.strip()

        if text.startswith("```"):
            parts = text.split("```")
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        summaries = json.loads(text)
        by_id = {s["id"]: s for s in summaries}

        for i, f in enumerate(findings, 1):
            entry = by_id.get(i, {})
            if "plain_english" in entry:
                f["plain_english"] = entry["plain_english"]
            if "cursor_prompt" in entry:
                f["cursor_prompt"] = entry["cursor_prompt"]

    except Exception as e:
        print(f"[summarizer] Gemini error: {e}")
        for f in findings:
            if not f.get("plain_english"):
                f["plain_english"] = f["message"]
            if not f.get("cursor_prompt"):
                f["cursor_prompt"] = (
                    f"In file `{f['file']}` line {f['line']}, fix this security flaw: {f['message']}."
                )

    return findings
