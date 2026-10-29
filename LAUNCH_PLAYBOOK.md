# 🚀 VibeCheck Viral Launch Playbook

This playbook outlines how to launch `npx vibecheck` on Twitter/X, Reddit, and Product Hunt to convert free users into \$49 paid audits.

---

## 1. The Core Twitter / X Launch Thread

Post this on Twitter with a 15-second terminal screen recording of `npx vibecheck` running:

### Tweet 1 (The Hook):
> I scanned 50 apps built with Cursor this week.
>
> Over 60% of them had an open Supabase database or leaked their `service_role` admin key in client code.
>
> When you vibe-code, AI prioritizes "it works" over "it's secure."
>
> So I built a free, 100% offline CLI tool to scan your private repo in 5 seconds:
>
> `npx vibecheck` 🧵👇

### Tweet 2 (The Lived Pain):
> Here's the #1 mistake Cursor makes with Supabase:
>
> It creates an RLS policy like:
> `CREATE POLICY ... USING (auth.role() = 'authenticated');`
>
> It looks secure because it says "authenticated".
> But it means ANY logged-in user can query or delete EVERY OTHER USER'S data.
>
> You won't notice until someone dumps your DB on Product Hunt day.

### Tweet 3 (The Solution & Trust):
> Most security tools want you to OAuth your private repo to an unknown web server.
>
> Hell no.
>
> `npx vibecheck` runs 100% locally on your machine.
> • 0 network requests
> • 0 code uploaded
> • Instant copy-paste SQL for Supabase Studio
> • Drops a surgical `.cursorrules` to stop Cursor from repeating the bug

### Tweet 4 (The Call to Action):
> Run it in your terminal right now:
>
> `npx vibecheck`
>
> If you're launching on Product Hunt this week and want a live external black-box attack on your staging URL to guarantee you're safe, grab Launch Insurance here: [your-link.com]

---

## 2. Reddit Playbook (r/SideProject, r/webdev, r/Supabase, r/nextjs)

**Title:** *I built a zero-trust local CLI to check if Cursor leaked your Supabase keys or RLS policies*

**Body:**
> Hey everyone,
>
> Like a lot of you, I've been building apps with Cursor and Next.js App Router. But after seeing horror stories of founders waking up to \$10,000 OpenAI bills or drained Supabase databases, I noticed AI coding models consistently make the same 4 architectural blunders:
> 1. Putting `SUPABASE_SERVICE_ROLE_KEY` in frontend files or `NEXT_PUBLIC_`
> 2. Permissive RLS: `auth.role() = 'authenticated'` allowing cross-user data scraping
> 3. Next.js Server Actions with `'use server'` that don't verify `auth.getUser()`
> 4. `getSession()` instead of `getUser()` in server middleware
>
> I built `npx vibecheck` — a lightweight CLI that runs 100% offline inside your private repo. It doesn't send a single byte of code anywhere. It just catches these exact mistakes, gives you the exact SQL to paste into Supabase Studio, and auto-generates a clean `.cursorrules` file.
>
> Free & MIT licensed. Just run `npx vibecheck` in your project folder.
> Would love your brutal feedback on what other vibe-coding bugs to add!

---

## 3. Product Hunt Launch Copy

* **Tagline:** Free pre-flight security scanner for vibe-coded apps
* **Target Audience:** Founders building with Cursor, v0, Bolt, Supabase & Next.js
* **Price:** Free core CLI / \$49 Live Black-Box Launch Insurance
