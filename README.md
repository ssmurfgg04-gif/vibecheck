# 🛡️ VibeCheck

> **"Vibe coding is fast. Vibe checking keeps you in business."**  
> *The offline health, security, and context auditor for AI-generated code (Cursor, Claude, Copilot, v0, Bolt).*

[![npm version](https://img.shields.io/badge/npm-vibecheck--scan-red.svg)](https://www.npmjs.com/package/vibecheck-scan)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero Network Calls](https://img.shields.io/badge/privacy-100%25%20offline-brightgreen.svg)](#-privacy--zero-telemetry)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-purple.svg)](#-cursor--claude-desktop-mcp-integration)

---

## ⚡ Instant Run (Zero Installation)

Run directly in any project root — **100% local, zero network calls, zero token costs, no credentials needed**:

```bash
npx vibecheck-scan
```

*(Or simply `npx vibecheck` if installed globally)*

---

## 🥊 How VibeCheck Outperforms Alternatives

| Capability | Generic LLM Pen-Testers | Manual Markdown Checklists | **VibeCheck** |
| :--- | :--- | :--- | :--- |
| **Speed** | 30s – 2min (slow LLM calls) | Manual human reading | **< 500ms (instant)** |
| **Privacy / Telemetry** | ❌ Sends your private code to 3rd-party APIs | ⚠️ Manual verification | **✅ 100% Offline (0 bytes sent)** |
| **Cost** | 💸 Requires paid API tokens | Free | **🎉 100% Free & Open Source** |
| **Actionable Fixes** | Hallucinates explanations | Broad suggestions | **Generates exact `.cursorrules` & SQL** |
| **CI / CD Automation** | Flaky & rate-limited | Impossible | **Native JSON output & GitHub Actions** |
| **AI Agent Native** | No standard interface | None | **Built-in Model Context Protocol (MCP)** |

---

## 🎯 What VibeCheck Catches

Generic linters check for whitespace and semicolons. VibeCheck was built specifically for traps created by AI code generators:

1. **Leaked Supabase `service_role` Key**: Catches admin secret keys exposed in client bundles or under `NEXT_PUBLIC_`.
2. **Permissive Supabase RLS**: Detects dangerous policies like `auth.role() = 'authenticated'` that allow any registered user to scrape or modify every other user's records.
3. **Unprotected Next.js Server Actions**: Flags `'use server'` mutations operating on databases without verifying `await supabase.auth.getUser()`.
4. **Hardcoded AI & Payment Secrets**: Catches exposed OpenAI (`sk-...`), Anthropic, and Stripe (`sk_live_...`) keys before they rack up billing spikes.
5. **Session Spoofing Risks**: Flags insecure `getSession()` calls in server middleware and guides you to use verified `getUser()`.

---

## 🤖 Cursor & Claude Desktop MCP Integration

VibeCheck is also a native **Model Context Protocol (MCP)** server. You can connect it directly to **Cursor** or **Claude Desktop** so your AI assistant audits its own code before suggesting diffs!

Add this to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "vibecheck": {
      "command": "npx",
      "args": ["-y", "vibecheck-scan", "--mcp"]
    }
  }
}
```

Now Claude / Cursor can natively invoke:
- `vibecheck_scan`: Deep audit of local files for security risks.
- `vibecheck_generate_rules`: Automatically drop a surgical `.cursorrules` file into the active workspace.

---

## 🛠️ CLI Options

```bash
# Scan a specific repository or subdirectory
npx vibecheck-scan ./my-app

# Machine-readable JSON output for CI/CD gates
npx vibecheck-scan --json

# Start MCP Server on stdio
npx vibecheck-scan --mcp

# Only generate surgical .cursorrules guardrails
npx vibecheck-scan --rules-only

# Simulate an external black-box attack on your live Supabase endpoint
npx vibecheck-scan --probe https://your-project.supabase.co your-anon-key
```

---

## 🔒 Privacy & Zero Telemetry

VibeCheck will **never** transmit your proprietary code, file names, or tokens over the internet.
- All AST & regex checks execute strictly in memory on your local CPU.
- Works entirely offline (on planes, air-gapped environments, or behind corporate firewalls).

---

## 🚦 GitHub Actions CI Pipeline

Add `.github/workflows/vibecheck.yml` to fail PRs that introduce vibe-coding security holes:

```yaml
name: VibeCheck Security Gate

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Run VibeCheck Audit
        run: npx vibecheck-scan --json
```

---

## 📦 Publishing to npm

If you maintain this package:
```bash
cd cli
npm login
npm publish --access public
```

---

## 📄 License

MIT © 2026 VibeCheck Contributors
