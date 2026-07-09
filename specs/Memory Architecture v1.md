# Memory Architecture v1 — Knowledge Capture System

Status: Proposed. Not yet approved. No implementation exists.

This specification refines the Knowledge Capture System proposal into an
implementation-ready architecture. It extends the existing Marcos OS
pipeline (Knowledge Layer → Context Layer → Capture Layer → Memory Layer →
Executive Layer) rather than replacing any part of it.

---

## 0. The Marcos OS Constitution

Some documents are not architecture — they are permanent identity. They
change only by explicit, deliberate decision, never as a side effect of a
sprint. This specification treats the following as constitutional:

* **Mission** — `MISSION.md`. Why Marcos OS exists and what it optimizes for.
* **Principles** — the design principles already in `ARCHITECTURE.md`
  (Drafts before permanence, Knowledge before intelligence, Executives own
  domains, Extend don't replace, …), plus the principle this revision adds:

  > Interfaces may change. The underlying knowledge model should remain
  > stable.

* **AI Roles** — the two-agent system in `CLAUDE.md` and
  `DEVELOPMENT_GUIDE.md` (Chief Systems Architect / Chief Builder /
  Repository Owner), governed by a constitutional constraint: no AI
  model's built-in memory is a source of truth. Marcos OS owns the
  project's memory; AI models synchronize *from* Marcos OS, they do not
  *act as* its memory.
* **Decision Framework** — the priority model (Faith → Family → Health &
  Safety → … → Convenience, defined in `specs/Memory Layer.md`) and the
  standing rule that architectural conflicts stop work and request
  guidance rather than being resolved unilaterally.
* **Memory Philosophy** — Draft before Active, archive instead of delete,
  and the raw capture as the permanent record beneath any extraction or
  interpretation of it (Sections 4–8 below).

The Constitution does not replace these documents — it names them as one
referenceable set, so any AI session can distinguish what defines the
project's identity (rarely changes) from what describes its current
architecture (this document) or its current state
(`PROJECT_STATE.md`, Section 10).

---

## 1. Goals and Non-Goals

### Goals

* No information captured in any AI conversation, email, or chat tool is
  ever permanently lost — even if extraction or categorization is wrong.
* A single, durable, vendor-neutral knowledge substrate — structured
  notes and frontmatter, versioned in Git — that any current or future
  AI model can read from and contribute to through defined interfaces.
  Obsidian is v1's interface to this substrate, not the substrate itself
  (Section 11).
* No AI model's built-in memory is treated as a source of truth. Marcos
  OS owns the project's memory; every AI session synchronizes from it
  (Section 10, Section 13).
* Knowledge stays organized and trustworthy as volume grows over years —
  via entity normalization and a Draft → Review → Active gate, the same
  discipline already proven in the Memory Layer.
* Engineering knowledge about Marcos OS itself (architecture decisions,
  session history) is captured with the same rigor as personal knowledge,
  enabling any AI session — Claude Code, ChatGPT, a future model — to
  resume work with full context.
* Extend `CapturePipeline`, `CaptureRouter`, `MemoryStore`, `ContextEngine`,
  `ContextProfileBuilder`, and the Event Bus. Introduce no parallel system.

### Non-Goals (v1)

* Automated, API-driven ingestion from every vendor (ChatGPT export API,
  Slack app, Gmail API). v1 is manual/semi-manual capture only.
* Fully automated LLM extraction and categorization with no human review.
  v1 keeps a human review gate on everything that reaches the vault.
* Semantic search, embeddings, or a vector database. Flagged as a future
  seam, not built.
* Multi-user or multi-tenant support. This is a single-person system.
* Live, bidirectional sync with any vendor's native memory feature. v1 is
  one-directional: capture in, export out.
* Automatic resolution of contradictory knowledge. v1 surfaces conflicts
  to Marcos; it does not adjudicate them.

---

## 2. System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                         SOURCE SYSTEMS                              │
│   ChatGPT · Claude · Gemini · Email · Slack · future tools          │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ Connector (manual v1 / automated v2+)
┌───────────────────────────▼─────────────────────────────────────────┐
│                    RAW CAPTURE ARCHIVE                              │
│   captures/raw/<source>/<year>/  — immutable, append-only            │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ KnowledgeExtractor (rule-based v1 / LLM v2)
┌───────────────────────────▼─────────────────────────────────────────┐
│                  KNOWLEDGE EXTRACTION PIPELINE                      │
│   ExtractedKnowledgeItem[]: Fact · Decision · Insight ·              │
│   ActionItem · Reference                                            │
└──────────────┬───────────────────────────────┬──────────────────────┘
               │ ActionItem                    │ Fact/Decision/Insight/Reference
┌──────────────▼──────────────────┐  ┌──────────▼────────────────────────┐
│   EXISTING CAPTURE PIPELINE      │  │  ENTITY NORMALIZATION              │
│   CapturePipeline → CaptureRouter│  │  Entity Registry (Reference/)      │
│   → DraftMemory (unchanged)      │  │  match alias → canonical entity    │
└──────────────┬──────────────────┘  └──────────┬────────────────────────┘
               │                                 │ CATEGORIZATION
               │                       ┌──────────▼────────────────────────┐
               │                       │  Draft Knowledge Notes             │
               │                       │  Capture Hub/Inbox/ (status=draft) │
               │                       └──────────┬────────────────────────┘
               │                                  │ Review (batched, human)
               │                       ┌──────────▼────────────────────────┐
               │                       │  PROMOTION                         │
               │                       │  obsidian/<category>/   OR         │
               │                       │  docs/decisions/ (engineering)     │
               │                       └──────────┬────────────────────────┘
               │                                  │ Git commit (Section 12)
┌──────────────▼──────────────────────────────────▼────────────────────┐
│           STRUCTURED KNOWLEDGE — the canonical model                  │
│   Markdown notes + frontmatter + Entity Registry, versioned in Git.   │
│   This is the source of truth. Storage format and tooling are        │
│   implementation details — not what the architecture commits to.      │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │
            ┌──────────────────▼────────────────────────┐
            │     SEMANTIC MEMORY LAYER (future seam)     │
            │  vector search · semantic retrieval ·       │
            │  knowledge graph traversal                  │
            │  NOT PART OF v1 — seam only (Section 15)    │
            └──────────────────┬────────────────────────┘
                               │
┌──────────────────────────────▼─────────────────────────────────────────┐
│                     INTERFACES (replaceable, Section 11)                │
│  Obsidian (v1 human interface) · ContextEngine (in-process AI access)   │
│  · ExportService (bundles for external AI Projects) · future UIs        │
└───────────────────────────────────────────────────────────────────────┘

  PROJECT_STATE.md is mandatory reading for every AI session, before any
  analysis or implementation begins — it sits beside this entire diagram,
  read first, regardless of which layer the session will touch (Section 10).
```

---

## 3. Canonical Sources of Truth

Each layer owns a distinct kind of truth. No two layers duplicate the same
fact:

| Layer | Canonical for | Mutability |
|---|---|---|
| Raw Capture Archive | What was actually said/written, verbatim | Immutable, append-only |
| Structured Knowledge (Active notes) | Current, reviewed knowledge — the canonical model | Edited via Draft→Active promotion only |
| `MemoryStore` (existing) | Actionable items — commitments, tasks, habits | Existing Draft→Active→Completed→Archived lifecycle, unchanged |
| Git history | How knowledge changed over time | Append-only by construction |
| `PROJECT_STATE.md` | What is true *right now* for engineering work | Overwritten each session; not historical |
| Entity Registry | Canonical name ↔ note mapping | Edited only during review |
| `docs/decisions/` (ADRs) | Why an architectural choice was made | Immutable once accepted; superseded, not edited |
| Obsidian | Nothing. It is an interface, not a source of truth. | Replaceable without changing any row above |
| Semantic Memory Layer (future) | Nothing. An index/retrieval seam over Structured Knowledge. | Not built in v1 (Section 15) |
| Any AI model's built-in memory (ChatGPT, Claude, Gemini, future) | Nothing, ever. | Read-only convenience at best; always resynchronized from Marcos OS |

**Obsidian is an interface, not the canonical system.** "Structured
Knowledge" in v1 happens to be stored as Markdown files with frontmatter,
browsed and edited through Obsidian — but the architecture's commitment
is to that knowledge model (notes, frontmatter schema, entity links, Git
history), not to Obsidian as a product. A future interface (custom app,
web dashboard, a different editor) can replace Obsidian by reading and
writing the same files; no canonical row in the table above changes.
This is the practical meaning of the principle stated in Section 0:
*interfaces may change, the underlying knowledge model should remain
stable.*

The Knowledge Capture System introduces **knowledge notes** (Fact,
Decision, Insight, Reference) as a new category distinct from the
existing **actionable memory** objects (Commitment, Task, Habit, etc.).
`ActionItem`-type extractions are routed into the existing
`CapturePipeline` unchanged — this system does not duplicate that logic.

---

## 4. Raw Capture Archive Design

**Location:** a new top-level `captures/raw/` directory, separate from
`obsidian/`, so the curated vault never accumulates raw transcript noise.

**Structure:** `captures/raw/<source>/<year>/<date>-<slug>-<id>.md`
(e.g. `captures/raw/chatgpt/2026/2026-06-30-marriage-planning-4f2a.md`).
Partitioned by source and year from day one — flat folders do not scale
to years of captures.

**Format:** Markdown with YAML frontmatter, body is the raw text
verbatim:

* `capture_id` — UUID4
* `source` — `chatgpt` / `claude` / `gemini` / `email` / `slack` / future
* `source_type` — `conversation` / `email_thread` / `message` / `document`
* `captured_at` — UTC timestamp
* `model` — model/participant identifier, when known
* `url` — source URL if one exists, optional
* `content_hash` — hash of the raw body, used for duplicate-capture
  detection at ingestion time

**Invariants:**

* Append-only. A raw capture file is never edited after creation.
  Corrections happen by adding a new capture or correcting the
  *extracted* knowledge note — never by rewriting history.
* Never deleted. If something is later judged sensitive or wrong, it is
  the extracted, reviewed note that changes — the raw record stands as
  evidence of what was actually said.
* Stored in the main Git repository in v1 (see Section 16 for the
  tradeoff this implies, and Section 15 for the v3 alternative).

---

## 5. Knowledge Extraction Pipeline

A `KnowledgeExtractor` is an interface, not an implementation: given a
`RawCapture`, it returns zero or more `ExtractedKnowledgeItem` records.
Multiple implementations can exist behind this one interface.

**`ExtractedKnowledgeItem` fields:**

* `item_type` — `Fact` / `Decision` / `Insight` / `ActionItem` / `Reference`
* `title` — short headline
* `body` — the distilled content
* `suggested_category` — best-guess vault category
* `suggested_entities` — names/things mentioned, for normalization
* `confidence` — 0.0–1.0, same scale already used by `DraftMemory`
* `source_capture_id` — backlink to the Raw Capture Archive entry

**v1 — rule-based extractor.** Heading detection, explicit markers
(`Decision:`, `Remember:`, `TODO:`), and keyword density — the same
evolutionary starting point `CaptureRouter` used before any AI
classification existed. Zero new dependencies.

**v2 — pluggable LLM extractor.** Same interface, different
implementation. Model-agnostic by construction: whichever model backs it
(OpenRouter, direct API, local model) is an implementation detail behind
the interface, never exposed to downstream stages.

`ActionItem`-typed results are hand off to the **existing**
`CapturePipeline`/`CaptureRouter`/`MemoryCommitService` chain unchanged.
Everything else proceeds to Entity Normalization (Section 6).

---

## 6. Entity Normalization Strategy

**Problem:** the same person, place, or project will be mentioned with
varied phrasing across hundreds of captures ("Sara," "my wife," "Sara
Vargas"). Without normalization, the vault accumulates duplicate,
fragmented notes instead of one canonical, growing note per entity.

**Entity Registry:** a single index file, `obsidian/Reference/entities.yaml`,
mapping canonical entity name → list of known aliases → vault file path.
This is an index over existing vault notes — it does not replace or
duplicate them. `Relationships/Sara.md` remains the canonical note; the
registry just knows "Sara," "my wife," and "Sara Vargas" all resolve to it.

**v1 — exact and alias matching.** During categorization, every
`suggested_entity` is matched against the registry (case-insensitive
exact match, then known-alias match). No fuzzy or semantic matching.

**Unmatched entities are not auto-created.** An extraction that
references an entity with no registry match surfaces in the Draft review
queue as "new entity?" rather than silently creating a new note. This
puts the one decision that actually requires judgment — is this a new
person/thing, or a new name for something that already exists — in front
of a human, while everything mechanical stays automated.

**v2 (deferred):** fuzzy/embedding-based alias suggestion to reduce
review burden as the registry grows. Not built in v1 — premature without
real usage data on how often aliasing actually causes friction.

---

## 7. Categorization Strategy

Categorization reuses the **existing** 18-folder vault taxonomy
(Identity, Business, Relationships, Finances, Health, …) and the
**existing** `CaptureRouter` extensible handler-chain pattern. No second
taxonomy is introduced.

**Two-pass resolution:**

1. **Entity-based routing.** If an extracted item resolved to a known
   entity (Section 6), it inherits that entity's existing category.
   This is the primary path and requires no classification logic of its
   own — it rides on the registry.
2. **Handler-chain fallback.** Items with no entity match are routed
   through keyword/heading handlers, identical in shape to
   `CaptureRouter`'s existing `_handle_commitment` / `_handle_observation`
   pattern. New handlers can be added the same way new capture handlers
   are added today — no change to the router's interface.

Items that plausibly belong to more than one category get a single
primary category (the file's location) plus wikilinks into the other
relevant notes — never duplicated across folders.

Engineering knowledge is categorized separately; see Section 9.

---

## 8. Draft → Review → Active Workflow

This mirrors the existing `DraftMemory` lifecycle
(`Draft → Active → Completed → Archived`), applied to knowledge notes
instead of actionable memory, with one additional terminal state:

```
Draft → Reviewed → Active → Archived
                 ↘ Discarded
```

| State | Meaning |
|---|---|
| `draft` | Created automatically by extraction + categorization. Lives in `Capture Hub/Inbox/`. |
| `reviewed` | Marcos has looked at it but not yet filed it (optional intermediate state for batch review sessions). |
| `active` | Promoted into its category folder in `obsidian/`. Canonical, trusted knowledge. |
| `archived` | Superseded or no longer current. Moved to `Archive/`, never deleted, frontmatter links to its replacement. |
| `discarded` | Judged not worth keeping as a vault note. Moved to `Capture Hub/Discarded/`. The raw capture is **not** affected — the original record persists regardless. |

**Review is batched, not per-item** (e.g. weekly), consistent with the
mission's "reduce mental load" principle — reviewing twenty drafts at
once costs less attention than twenty interruptions.

**Event Bus integration (extends, does not duplicate, the existing five
event types):**

* `KNOWLEDGE_DRAFT_CREATED`
* `KNOWLEDGE_PROMOTED`
* `KNOWLEDGE_ARCHIVED`

These follow the same `Event` model already defined in `core/event_bus.py`.

---

## 9. Engineering Knowledge vs. Personal Knowledge

Two lanes, one mechanism. Both flow through the same
Capture → Extract → Normalize → Categorize → Review → Promote pipeline;
only the destination differs.

| | Personal knowledge | Engineering knowledge |
|---|---|---|
| Source conversations | Life conversations with any AI, email, Slack | ChatGPT architecture sessions, Claude Code sessions |
| Destination | `obsidian/<category>/` | `docs/decisions/` (new) |
| Granularity | One atomic note per durable idea | One immutable record per decision |
| Mutability | Active notes are edited in place; superseded by archiving | Never edited after acceptance; superseded by a new, numbered ADR with a backlink |
| Existing precedent | Existing 18-category vault | None yet — `docs/` exists as a placeholder directory today |

**Architecture Decision Records (ADRs):** `docs/decisions/0001-<slug>.md`,
sequentially numbered, one decision per file. This gives Marcos OS itself
the same "never delete, archive instead" discipline the Memory Layer
already enforces for personal commitments — applied to *why the system
is built the way it is built*.

`ROADMAP.md`, `HANDOFF.md`, and `CHANGELOG.md` are unchanged in purpose:
they remain hand-curated summaries. ADRs are their source material, the
same way raw `Recommendation` objects are the source material for a
curated `MorningBrief`.

---

## 10. PROJECT_STATE.md and Session Continuity

A new file at the repository root: `PROJECT_STATE.md`.

**Distinct from existing docs — does not duplicate them:**

* `HANDOFF.md` — onboarding reference, changes rarely, explains *how the
  system works*.
* `ROADMAP.md` — sprint history and plan, append-only, explains *what has
  been built and what's next*.
* `PROJECT_STATE.md` — a short, frequently overwritten snapshot of
  *what is true right now*: current sprint, last session date and
  one-paragraph summary, decisions awaiting approval, known-broken
  things, the single next action. Target: readable in under 60 seconds.

It links into `ROADMAP.md`/`HANDOFF.md`/`docs/decisions/` rather than
restating their content.

**Mandatory read, every session.** `PROJECT_STATE.md` is not optional
context — it is the required first step of every AI session, before any
analysis or implementation begins. Every AI engineer (Claude Code,
ChatGPT, or a future model) synchronizes with `PROJECT_STATE.md` first.
This is the practical mechanism behind the Constitution's AI Roles
constraint (Section 0): the AI is not relying on its own memory of past
sessions — it is reading the file Marcos OS maintains as ground truth.

**Update trigger:** added to the existing "After a sprint" checklist
already defined in `CONTRIBUTING.md`, rather than introducing a new
process. Any AI session — Claude Code today, ChatGPT in an architecture
session, a future model — reads `PROJECT_STATE.md` first and gets
immediate orientation without re-reading the full repository.

---

## 11. Obsidian Integration

**Obsidian's role: interface, not foundation.** Obsidian is chosen for v1
because it is a capable, local-first, plain-Markdown-native editor with a
free graph view — not because the architecture depends on it. Nothing in
this specification stores data in an Obsidian-proprietary format; notes,
frontmatter, and wikilinks are all plain text, readable without Obsidian
installed. If Obsidian is ever replaced, the only required work is
pointing a new interface at the same files — Sections 3–9 (the knowledge
model itself) do not change.

No change to the existing principle that the vault is plain Markdown,
human-owned, and AI-read. The Knowledge Capture System becomes an
additional **writer**, but only through the Draft → Review → Active gate
— it never writes directly to `obsidian/` category folders.

**New folders (extending, not replacing, the existing `Capture Hub/`):**

* `Capture Hub/Inbox/` — draft knowledge notes awaiting review
* `Capture Hub/Discarded/` — rejected drafts, kept for traceability

**New reference file:**

* `Reference/entities.yaml` — the Entity Registry (Section 6)

No new top-level vault folders are introduced — consistent with
`CONTRIBUTING.md`'s rule against creating new top-level directories
without an explicit architectural decision. Obsidian's native graph view
and backlinks become the human browsing interface for the knowledge
graph; no custom UI is built.

---

## 12. GitHub Integration

**v1:** every Draft → Active promotion is one commit with a structured
message: `knowledge: <title> [<source>] (<category>)`. Direct-to-main,
consistent with the current "no branch strategy yet" stance in
`DEVELOPMENT_GUIDE.md`.

**v2 (proposed, not required for v1):**

* Captures land on a `capture/<date>` branch; promotion opens a PR.
  Marcos reviews and approves via the GitHub UI — usable from any
  device, which matters because captures originate from many devices
  and AI tools.
* GitHub Issues track specific "needs a human decision" items (e.g.
  ambiguous entity matches) instead of a custom review UI.

**v3 (deferred):**

* GitHub Actions validate frontmatter schema on PR and regenerate export
  bundles (Section 14) on merge to `main`. CI-only — `marcos-core`
  remains dependency-free per existing convention.

---

## 13. Multi-Model AI Support (ChatGPT, Claude, Gemini, future)

Interface-first, per the stated requirement to prefer interfaces over
vendor-specific implementations:

* `KnowledgeExtractor` (Section 5) — any model can implement it. v1's
  implementation requires no model at all (rule-based).
* `Exporter` (Section 14) — any consumer's required bundle shape can
  implement it without touching the canonical Structured Knowledge.

**No model gets special access or a special format.** The vault is plain
Markdown; every model — present or future — consumes it identically, via
either the in-process `ContextEngine` (Marcos OS itself) or an export
bundle (external AI tools, Section 14). Adding support for a new AI
vendor in the future means writing one new `Connector` and, if desired,
one new `KnowledgeExtractor` implementation — it never requires changing
the extraction, normalization, categorization, or review stages.

**No AI model's built-in memory is a source of truth.** ChatGPT's memory,
Claude's Projects knowledge, Gemini's saved context, and any future
model's equivalent feature are, at most, a convenience cache of what was
last exported to them (Section 14) — never authoritative, and never a
substitute for the mandatory `PROJECT_STATE.md` synchronization (Section
10). Marcos OS owns the project's memory; every model synchronizes
*from* it. This is the Constitution's AI Roles constraint (Section 0)
applied concretely to this integration point.

---

## 14. Export Pipeline for AI Projects

Most external AI tools (ChatGPT Projects, Claude Projects, Gemini Gems)
cannot read a live filesystem — they consume uploaded or pasted files.
An `ExportService` closes this gap: it compiles Structured Knowledge into
upload-ready bundles, so the one canonical knowledge model feeds every AI
tool without per-tool manual re-curation.

**v1:** on-demand, manually triggered. One combined Markdown digest per
requested category (e.g. "export everything in Business").

**v2:** scheduled regeneration (via GitHub Actions, Section 12),
producing versioned export artifacts so a bundle's freshness is always
known.

**v3 (deferred, not designed here):** per-tool optimized formats — e.g.
chunking for upload size limits. Explicitly not designed in v1; building
this before real usage reveals which tools actually need it would be
premature complexity.

---

## 15. Scalability Roadmap

**v1 — Foundation.** Manual capture, rule-based extraction, manual
categorization fallback (entity-routing where possible), manual batched
review, Raw Capture Archive, `PROJECT_STATE.md`, ADRs in
`docs/decisions/`. Zero new external dependencies — consistent with
`marcos-core`'s stdlib-only convention.

**v2 — Automation.** Pluggable LLM-based `KnowledgeExtractor`
(model-agnostic interface, Section 13), fuzzy entity matching, GitHub
PR-based review (Section 12), scheduled export bundles, first automated
`Connector` (e.g. a ChatGPT export-file importer).

**v3 — Scale.** The Semantic Memory Layer (Section 2) is built: indexed
or semantic retrieval — vector search, embeddings, or knowledge graph
traversal — inserted between Structured Knowledge and the Interfaces
tier, behind a stable retrieval interface so `ContextEngine` and every
other consumer are unaffected by what powers retrieval underneath. This
is the same kind of swap-in-place seam already documented for
`MemoryStore`'s future PostgreSQL backend, applied here to knowledge
retrieval. Automated connectors for all major sources. A raw-archive
cold-storage strategy if `captures/` growth makes the main Git history
unwieldy. Any database-backed knowledge index is explicitly tied to the
existing Sprint 011 PostgreSQL plan rather than a second, separate
database track.

---

## 16. Risks and Tradeoffs

* **Review bottleneck.** If batched review lapses, `Capture Hub/Inbox/`
  grows unbounded. Mitigation deferred to v2 (a recurring nudge via the
  Event Bus); flagged as a real risk now, not solved in v1.
* **v1 extraction is noisy.** Rule-based extraction will have low
  recall/precision. Accepted tradeoff: the Raw Capture Archive guarantees
  nothing is *lost*, only possibly *mis-filed* — recall is sacrificed for
  simplicity in v1, not for data safety.
* **Entity duplication risk** if the registry isn't maintained. Mitigated
  by surfacing ambiguous matches for human judgment instead of
  auto-creating entities, but the registry can still drift if reviews are
  skipped.
* **Git repository growth.** Raw captures accumulate indefinitely in the
  main repo under v1. Mitigated structurally (dedicated `captures/`
  directory, partitioned by source/year) but not solved long-term until
  v3's cold-storage option is evaluated.
* **Sequencing/scope risk.** This specification spans personal knowledge,
  engineering knowledge, multi-model export, and GitHub workflow at once.
  Recommend implementing in stages (see Section 17) rather than as one
  sprint.
* **Sensitivity of raw captures.** Email threads, financial, and health
  conversations may be captured verbatim into plain Git history with no
  encryption-at-rest in v1. This is a deliberate simplicity tradeoff, not
  an oversight — flagged as an open decision in Section 17 rather than
  solved preemptively.

---

## 17. Open Architectural Decisions

These require a decision from the Chief Systems Architect and/or
Repository Owner before implementation begins:

1. **Engineering knowledge location.** Confirm `docs/decisions/` (this
   spec's proposal) versus routing into the existing `obsidian/Systems/`
   folder.
2. **v1 extraction method.** Confirm rule-based extraction is acceptable
   for v1, or decide whether to pull LLM-based extraction forward ahead
   of the already-planned Sprint 012 OpenRouter integration.
3. **GitHub review model.** Direct-to-main commits indefinitely, or
   adopt the PR-based review flow (Section 12) — and if so, on what
   timeline relative to v2.
4. **Raw capture storage location.** Confirm raw captures belong in the
   main repository (this spec's default), or should be routed to a
   separate repository/storage to avoid mixing potentially sensitive raw
   content with the curated, shareable vault history.
5. **Review cadence.** Daily, weekly, or ad hoc — affects whether the
   Inbox-growth risk (Section 16) needs an automated nudge sooner than v2.
6. **Sequencing against existing roadmap work.** Where this sprint lands
   relative to the still-open Sprint 010 documentation reconciliation and
   the planned Sprint 011 PostgreSQL integration (which Section 15's v3
   explicitly depends on).

---

This specification is implementation-ready pending answers to Section 17.
No code has been written. Awaiting review and approval.
