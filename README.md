# 🛡️ VibeCheck

**Pre-flight security scanner for vibe-coded apps.**  
Detects leaked admin keys, open Supabase RLS policies, and unauthenticated Next.js Server Actions before you launch.

---

## ⚡ Quick Start

Run instantly in your project root — 100% locally, no installation, zero network requests:

```bash
npx vibecheck
```

### Options
```bash
# Scan a specific directory
npx vibecheck ./my-nextjs-app

# Only inject the surgical .cursorrules guardrails file
npx vibecheck --rules-only

# Simulate an unauthenticated external black-box attack on your live Supabase database
npx vibecheck --probe https://your-project.supabase.co your-anon-key
```

---

## 🎯 What VibeCheck Catches

Generic linters check for code style. VibeCheck was built strictly for the modern AI stack (Cursor, v0, Bolt, Next.js, Supabase):

1. **Leaked Supabase `service_role` Key**: Catches admin secret keys exposed in client bundles or under `NEXT_PUBLIC_`.
2. **Permissive Supabase RLS**: Detects dangerous policies like `auth.role() = 'authenticated'` that allow any registered user to scrape or modify every other user's records.
3. **Unprotected Next.js Server Actions**: Flags `'use server'` mutations operating on databases without verifying `await supabase.auth.getUser()`.
4. **Hardcoded AI & Payment Secrets**: Catches exposed OpenAI (`sk-...`), Anthropic, and Stripe (`sk_live_...`) keys before they rack up billing spikes.
5. **Session Spoofing Risks**: Flags insecure `getSession()` calls in server middleware and guides you to use verified `getUser()`.

---

## 🏗️ Architecture

```
vibecheck/
├── cli/                 # The 100% offline local CLI tool (npx vibecheck)
│   ├── bin/vibecheck.js # Zero-dependency scanner & live probe simulator
│   └── package.json     # Ready for npm publish
│
├── landing/             # High-converting landing page ($49 Launch Insurance wedge)
│   └── index.html
│
├── frontend/            # Optional web-based GUI scanner
│   └── index.html
│
├── backend/             # Optional FastAPI server for remote/CI scans
│   ├── main.py
│   ├── scanner.py
│   └── summarizer.py
│
└── LAUNCH_PLAYBOOK.md   # Viral Twitter & Reddit launch strategy
```

---

## 📦 How to Publish the CLI to npm

1. Navigate to the CLI directory:
   ```bash
   cd cli
   ```
2. Log in to your npm account:
   ```bash
   npm login
   ```
3. Publish publicly:
   ```bash
   npm publish --access public
   ```
4. Now anyone anywhere in the world can run `npx vibecheck` directly in their terminal!

---

## 📄 License
MIT
