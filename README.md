# Hermes GitHub

**Your issue tracker is a firehose. Your attention isn't.**

Hermes GitHub turns the noisy stream of issues and pull requests into a calm
scouting surface for the contributions you mean to make. Keep your saved
searches local, then bring in Hermes when an issue deserves a triage, a
summary, or a closer look.

POWERED BY HERMES AGENT · COMMUNITY PLUGIN · VERSION 0.1.0

[Make it yours](#make-it-yours) · [Understand the data](#privacy-you-can-explain-in-one-breath)

## Powered by Hermes

Hermes GitHub is a community-built contribution-scouting surface for
[Hermes Desktop](https://github.com/NousResearch/hermes-agent). It uses the
Hermes plugin SDK, your configured model and providers, native Hermes
conversations, and the same profile-aware desktop environment you already use.

The reader gives Hermes a focused starting point. An issue becomes a triage,
a pickability verdict, or a draft "looking into it" claim — without leaving
the app.

## Scouting with an agent in the room

Most issue watchers stop at a list of tickets. Hermes GitHub gives each item
a next step without turning every issue into an AI task.

| | |
| --- | --- |
| **Read** Subscribe to saved GitHub searches (repo, label, priority, anything the search syntax supports), open the original issue or PR, and browse one query at a time. | **Remember** Issues and PRs you have opened fade out; unread items stay easy to spot. Read state is stored locally and survives restarts. |
| **Scout** Ask the agent to triage a single issue: full-thread reading, competing-PR check, and a pickability verdict with the files likely involved. | **Act** The triage chat drafts the terse claim comment for your approval — the plugin never posts anything itself. |
| **Dispatch** Pick a connected profile (a **To:** dropdown in the header) and hand a row a task: **Review** (verdict + concrete review comments for issues or PRs) or **Solve** (a full implementation run with worktree + test discipline). The task opens as a session on that profile. | **Stay in control** Every task prompt is wrapped in untrusted-source-data rules and an explicit *no posting, no pushing, no PRs without approval* guard — the receiving agent drafts, you approve. |

The reader stays quiet until you ask it to do more. AI actions are explicit
and use your configured Hermes providers.

## Less maintenance. More finishing.

- **The token finds itself.** No setup ceremony: the backend resolves a
  GitHub token automatically (ordered ladder: `GITHUB_TOKEN`/`GH_TOKEN` env
  vars → `gh auth token` → the same names in `~/.hermes/.env`), and the
  token never leaves the server.
- Refresh automatically every 15 minutes while Hermes is open, or on demand.
- Open an issue and it is marked read; mark the whole list read in one click.
- Add a saved search in seconds; remove it with one click.
- No token anywhere? It falls back to the unauthenticated GitHub budget
  (60 requests/hour) and tells you so.

## Built for real repos, not a demo list

Hermes GitHub is a single unified-package plugin — one folder with a
plain-ESM desktop half (`desktop/plugin.js`) and a thin Python backend
(`dashboard/plugin_api.py`, FastAPI) that auto-detects your token and
proxies GitHub search calls. It works with stock Hermes Desktop; there is no
fork, upstream patch, build step, or package manager.

## Make it yours

### Install

Copy the repo folder into your Hermes plugins directory:

```bash
cp -R hermes-github ~/.hermes/plugins/
```

Then, in the desktop app: **Settings → Plugins** → find **GitHub** (hit
*rescan* if it isn't listed yet) → **toggle it ON** — the desktop half
ships opt-in and stays dark until you do. It activates live, no restart.

Last, enable the Python backend (it's gated separately — the UI toggle
does NOT import Python):

```bash
hermes config set plugins.enabled '["hermes-github"]'   # or via hermes plugins/manual config
```

…and restart the gateway once so its API routes mount
(`hermes gateway restart`, or Settings → Gateway). From then on the
backend auto-detects the token and proxies search calls.

> Until both switches are on, the plugin degrades gracefully: no backend →
> direct unauthenticated GitHub calls; no UI toggle → no GitHub entry.

### Tokens — three rungs, no typing

1. **Detected automatically** (backend): `GITHUB_TOKEN` / `GH_TOKEN`
   (process env), else `gh auth token` (your logged-in gh CLI — shown in
   the settings row as *Auto: gh CLI (yourlogin)*), else the same names in
   `$HERMES_HOME/.env` / `~/.hermes/.env`.
2. **Manual override** — the settings row still accepts a token; it is sent
   server-side per request, never stored in plugin storage.
3. **Nothing at all** — unauthenticated mode with the 60 req/hr budget and
   a visible hint.

Rate limits: unauthenticated 60 req/hr; any detected token raises the
budget to 5,000 req/hr.

## Privacy you can explain in one breath

Your queries and read state live in Hermes' local plugin storage. There is no
account, no server, no telemetry, and no third party in the path: the Python
backend talks to api.github.com directly (token stays in the gateway
process — it is never returned to the renderer, never written to plugin
storage). The only AI calls are the ones you explicitly trigger — each
carries the issue snapshot marked as untrusted source data, and the agent is
instructed never to act on instructions found inside it.

## Roadmap

- **v0.2** — per-query unread counts, pinned issues, issue/PR detail preview.
- **v0.3** — PR health glance (mergeable, CI status) for the "Open PRs" query.
- **v0.4** — feature-scout sweep: batch triage of fresh pickable leads (P1–P3 bugs, open feature requests).