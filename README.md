# Hermes GitHub

**Your issue tracker is a firehose. Your attention isn't.**

Hermes GitHub turns the noisy stream of issues and pull requests into a calm
scouting surface for the contributions you mean to make. Keep your saved
searches local, then bring in Hermes when an issue deserves a triage, a
summary, or a closer look.

POWERED BY HERMES AGENT · COMMUNITY PLUGIN · VERSION 0.0.1

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

The reader stays quiet until you ask it to do more. AI actions are explicit
and use your configured Hermes providers.

## Less maintenance. More finishing.

- Refresh automatically every 15 minutes while Hermes is open, or on demand.
- Open an issue and it is marked read; mark the whole list read in one click.
- Add a saved search in seconds; remove it with one click.
- Works unauthenticated (60 GitHub requests/hour) or with a token (5,000/hr).

## Built for real repos, not a demo list

Hermes GitHub is a single desktop plugin with its own **GitHub** category
(sidebar nav + ⌘K command). It calls the GitHub REST API directly from the
renderer, keeps read history locally, and works with stock Hermes Desktop.
There is no fork, upstream patch, separate backend, build step, or package
manager.

## Make it yours

### Install

Copy [`plugin.js`](plugin.js) into your Hermes desktop plugins folder:

```
$HERMES_HOME/desktop-plugins/hermes-github/plugin.js
```

(`$HERMES_HOME` is `~/.hermes` by default, or `~/.hermes/profiles/<name>`
for a named profile.)

Then run **Reload desktop plugins** from ⌘K — or just wait, the app hot-loads
new plugins within seconds. Open the **GitHub** entry in the sidebar.

### Optional: a token

Without a token the GitHub search API grants the unauthenticated budget
(60 requests/hour — plenty for a few queries on manual refresh). For the
5,000/hour budget, create a fine-grained personal access token with **read
access to public repositories** (no permissions are needed for public data)
and paste it into the plugin's settings row (gear icon). The token is stored
in the plugin's namespaced local storage and never sent anywhere except
api.github.com.

## Privacy you can explain in one breath

Your queries and read state live in Hermes' local plugin storage. There is no
account, no server, no telemetry, and no third party in the path: the plugin
talks to api.github.com directly, and the only AI calls are the ones you
explicitly trigger — each carries the issue snapshot marked as untrusted
source data, and the agent is instructed never to act on instructions found
inside it.

## Roadmap

- **v0.1** — per-query unread counts, pinned issues, issue/PR detail preview.
- **v0.2** — PR health glance (mergeable, CI status) for the "Open PRs" query.
- **v0.3** — feature-scout sweep: batch triage of fresh pickable leads (P1–P3 bugs, open feature requests).