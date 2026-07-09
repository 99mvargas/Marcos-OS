# PROJECT_STATE.md — Specification

Status: Approved. `PROJECT_STATE.md` itself has not yet been created in
the repository — this document specifies it.

This refines the sketch introduced in `specs/Memory Architecture v1.md`
§10 into the authoritative, standalone specification. Once
`PROJECT_STATE.md` is created, §10 of that document should be updated to
point here rather than re-describing it.

---

## 1. Purpose

`PROJECT_STATE.md` is the single, authoritative answer to **"what is true
about this project right now."** It exists so that any AI session —
Claude Code, ChatGPT, a future model, after five minutes or five months —
can orient itself without re-reading the repository or relying on its own
memory of prior sessions. It is the concrete file that satisfies the
Constitution's AI Roles principle (Memory Architecture v1 §0): *Marcos OS
owns the project's memory; AI models synchronize from it.*

It is a **snapshot**, not documentation and not history. It is optimized
to be read first, read fast, and acted on immediately.

---

## 2. Ownership — Who Updates It

* **Claude Code (Chief Builder)** is the primary writer, at the
  checkpoints defined in Section 3.
* **Marcos** may edit it directly at any time — to redirect priority,
  answer a pending decision, or leave a note for the next session — since
  he is the Repository Owner and this file represents ground truth he can
  correct without going through an AI.
* **ChatGPT (Chief Systems Architect)** does not write it directly,
  consistent with the existing two-agent system. Architectural decisions
  it makes reach this file only after Claude Code captures and reflects
  them.
* Exactly one mechanical writer (Claude Code, at session end) plus one
  authority override (Marcos, any time) — never two AIs updating it
  concurrently.

---

## 3. Update Triggers — When It Is Updated

* At the **end of every Claude Code session**, extending the existing
  "After a sprint" checklist in `CONTRIBUTING.md` — at session
  granularity, not only sprint granularity, since not all work maps
  cleanly to a full sprint.
* Immediately whenever: the current sprint changes, a decision is made
  that the next session needs to know about, something becomes broken or
  blocked, or a session ends with unfinished work.
* **Not updated continuously mid-session.** Moment-to-moment progress
  belongs in `CURRENT_TASK.md` (Section 7); `PROJECT_STATE.md` changes
  only at session boundaries, keeping it stable enough to be a true
  snapshot.

---

## 4. Audience — Who Reads It

* Every AI session, of any kind, as the **mandatory first read** before
  any analysis or implementation — already a hard requirement per
  Memory Architecture v1 §10.
* Marcos, for a fast status check without digging through `ROADMAP.md` or
  `HANDOFF.md`.
* It is human/AI-readable prose, not a machine-readable data file — no
  application code depends on it at this stage.

---

## 5. Required Contents

A fixed, minimal schema — not open-ended notes. Two sections
(Repository Status, Session Objective) were added in this revision to
give every session immediate Git awareness and an unambiguous definition
of success before any work begins.

* **Repository Status**
  * Current Branch
  * Working Tree Status — clean, or dirty with a brief note
  * Mechanical, not narrative: derived from `git status`, not authored —
    costs almost nothing against the 60-second budget despite being a
    new section.
* **Session Objective**
  * Objective — one line: what this session is trying to accomplish
  * Definition of Done — one line: how we'll know it's complete
  * Set once at the start of a session so "what does success look like"
    is never ambiguous or renegotiated mid-session.
* **Current Sprint** — number + name, a pointer into `ROADMAP.md`
* **Last Session** — date + one-paragraph summary of what happened
* **Current Task** — link to `CURRENT_TASK.md` if something is in
  flight, or "none — idle"
* **Decisions Awaiting Approval** — short bullets, each answerable in one
  sentence
* **Known Broken / Blocked** — short bullets, each linking out for detail
  rather than explaining inline
* **Next Action** — the single next concrete, tactical step. When a
  Session Objective is active, this may simply restate the first unmet
  criterion of its Definition of Done — the two fields are related, not
  duplicated: Objective/Definition of Done set the destination, Next
  Action is the next step toward it.

---

## 6. Excluded Contents

* Full sprint history → `ROADMAP.md`
* How the system works → `ARCHITECTURE.md` / `HANDOFF.md`
* Why a past decision was made → `docs/decisions/` (ADRs)
* Version-by-version release history → `CHANGELOG.md`
* Anything permanently true → the Constitution documents (`MISSION.md`,
  `CLAUDE.md`, etc.) — this file is for what's true *now*, not what's
  always true
* Granular in-progress task mechanics → `CURRENT_TASK.md`
* Long prose, code snippets, diffs
* **Stale entries.** This file does not accumulate — it is overwritten,
  not appended to. An item that's no longer current is deleted at the
  next update, not left to rot.

---

## 7. Relationship to Other Documents

| Document | Role | Relationship to `PROJECT_STATE.md` |
|---|---|---|
| `ROADMAP.md` | Append-only sprint history + plan | "Current Sprint" is a pointer into it — never restated |
| `HANDOFF.md` | Onboarding reference, changes rarely | Read for deep context when *onboarding*; `PROJECT_STATE.md` is read to *resume* — different jobs, no duplication |
| `CHANGELOG.md` | Version/release history | Orthogonal axis (release-level, not session-level) — no direct coupling |
| `CURRENT_TASK.md` (proposed) | Granular, in-flight task state | The inner, more volatile layer. `PROJECT_STATE.md` links to it rather than containing it; on task completion its contents fold into "Last Session" and the file resets to idle |
| `ARCHITECTURE.md` | How the system is structured | Permanent reference, like `HANDOFF.md`. Never duplicated here — if a session reveals architecture needs updating, that becomes the "Next Action," not an inline explanation |

This forms a stack, narrowest and most volatile at the bottom:

```
Constitution (permanent)
  → ARCHITECTURE.md / HANDOFF.md (structural, rarely changes)
    → ROADMAP.md (append-only history + plan)
      → PROJECT_STATE.md (current snapshot)
        → CURRENT_TASK.md (in-flight, most granular)
CHANGELOG.md sits on its own axis — release history, not session history.
```

---

## 8. Minimizing Context Loss Between Sessions

* The mandatory-first-read rule means no session starts blind.
* The strict size cap (Section 10) makes the file something that gets
  *fully read*, not skimmed or skipped.
* Repository Status prevents a session from assuming a branch or tree
  state that's no longer true — e.g. resuming after Marcos made local
  changes outside the AI session.
* Definition of Done anchors what "finished" means even if a session is
  interrupted and resumed later, preventing scope drift across the gap.
* The Next Action line removes ambiguity about where to start — no
  inference required.
* "Decisions Awaiting Approval" prevents re-litigating settled questions
  or silently stalling on forgotten ones.
* `CURRENT_TASK.md` narrows the recovery gap to *within* a session, not
  just between sessions.
* Linking out to `ROADMAP.md`/`HANDOFF.md`/ADRs instead of restating them
  avoids drift — a stale link is obviously stale; a stale summary is a
  silent lie.

---

## 9. Minimizing What Marcos Needs to Explain or Repeat

* Because every session reads this file first, Marcos never has to
  verbally re-brief "where we left off."
* Repository Status removes "what branch are we on, is the tree clean" —
  it's already visible, no need to ask or run a command.
* Session Objective means Marcos states the goal once, in the file,
  rather than restating it verbally each time work resumes; Definition
  of Done means "done" doesn't get renegotiated mid-session.
* "Decisions Awaiting Approval" lets him clear pending questions in one
  pass instead of being asked the same thing across multiple sessions.
* Because he can edit the file directly, he can leave instructions for
  the next session asynchronously, without a live conversation.
* "Known Broken / Blocked" means he doesn't have to repeat the same
  warning every time a new session starts.

---

## 10. Size Discipline — The 60-Second Rule

* Fixed sections only — no open-ended prose blocks.
* Each bullet list capped (e.g. ≤5 items, ≤1 line each); anything needing
  more is linked out, not inlined.
* Target size: roughly one screen (~45 lines, accounting for the two
  sections added in this revision). Exceeding it is a signal to prune at
  the next update — old or resolved items are cut, not archived in place.
* Repository Status and Session Objective are mechanical/terse by design
  (a branch name, a clean/dirty flag, two one-line fields) — they add
  immediate orientation without meaningfully taxing the read budget.
* The file alone should convey the headline state; links exist for the
  remaining detail, not for things needed to understand the snapshot
  itself.

---

## 11. Template

```
# Project State

Last updated: <date> by <Claude Code | Marcos>

## Repository Status
- Current Branch: <branch>
- Working Tree: <clean | dirty — brief note>

## Session Objective
- Objective: <one line — what this session is trying to accomplish>
- Definition of Done: <one line — how we'll know it's complete>

## Current Sprint
<number> — <name> (see ROADMAP.md)

## Last Session
<date> — <one paragraph: what happened>

## Current Task
<link to CURRENT_TASK.md, or "None — idle">

## Decisions Awaiting Approval
- <one line>

## Known Broken / Blocked
- <one line, link to detail if needed>

## Next Action
<one line>
```

---

This specification is implementation-ready. `PROJECT_STATE.md` itself has
not been created. Awaiting approval before doing so.
