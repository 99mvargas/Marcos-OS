# Development Guide

Onboarding for a new AI developer session. Teaches how Marcos OS is built —
not how sessions are run (see `docs/ENGINEERING_RULES.md` for that) and not
what's currently true (see `PROJECT_STATE.md` for that).

## Architecture

Marcos OS has three independent tracks in one repository:

- `apps/marcos-dashboard/` — the active track. A React 19 + Vite SPA, entirely
  mock-data driven, no backend yet. This is where current sprint work happens.
- `apps/marcos-core/` — an earlier-phase Python executive/memory engine. Not
  wired to the dashboard. Do not touch unless a task explicitly targets it.
- `docker/` — self-hosted infrastructure (Portainer, Jellyfin) that the
  dashboard links out to. Home Assistant is external, not containerized here.

The dashboard is a thin, typed presentation layer over mock data today. The
architecture is deliberately built so that mock data can be swapped for real
integrations (Plaid, Home Assistant, Docker APIs) later without UI rewrites —
see Provider Pattern below.

## Repository Philosophy

- The repository is the only source of truth — never conversation memory.
- Types come first. Every domain (Finance, Infrastructure, ...) gets a typed
  model before it gets a UI or a real integration.
- Extend, don't rewrite. New features add files; they rarely change existing
  ones beyond wiring (a route, an import, a PROJECT_STATE.md update).
- Nothing is invented. Mock data uses honest placeholders (0, null, "Not yet
  synced") — never fabricated numbers or dates.

## Folder Organization

```
apps/marcos-dashboard/src/
  types/            domain models, one file per domain (e.g. finance.ts)
  data/mock/         mock data instances, one file per domain, isolated from UI
  features/<domain>/ pages + domain-specific components
    <domain>-page.tsx
    components/      (or a subfolder like statement-vault/ for a sub-feature)
  components/ui/     shared primitives (Card, Badge, Button, ...) — reuse, don't fork
  components/layout/ AppShell, TopBar, BottomNav — global chrome
  lib/               small shared utilities (format.ts, utils.ts)
  hooks/             shared React hooks
```

A new domain = one `types/<domain>.ts`, one `data/mock/<domain>.ts`, one
`features/<domain>/<domain>-page.tsx`, one route in `App.tsx`.

## Executive Pattern

Marcos OS is organized as an "Executive Operating System": each life/business
domain (Finance, Infrastructure, Knowledge, Business, Purchasing, Health) is
modeled as an Executive with its own route, types, and mock data. Home is the
landing surface, not an Executive itself. The `ExecutivesNav` component on the
Home page is the single directory of all Executives; new ones start there as
disabled "Coming Soon" tiles until a domain is built out, then get promoted to
a working link. Do not build an Executive's UI before its domain types exist.

## Provider Pattern

Each domain separates **shape** from **source**:

1. A typed model (`types/<domain>.ts`) defines what the data looks like.
2. Mock data (`data/mock/<domain>.ts`) satisfies that shape with placeholders.
3. A future **Provider** (e.g. a Plaid adapter, a `StatementParser`) implements
   a narrow interface that produces the same typed shape from a real source.
4. UI components only ever consume the typed shape — never a specific
   provider — so swapping mock data for a real provider is a data-source
   change, not a UI change.

When a task says "architecture only," it means: define the interface and a
placeholder implementation of step 3, not real steps 3's internals (no OCR,
no live API calls, no parsing) until a separate task asks for it.

## Mock Data Rules

- One mock file per domain under `src/data/mock/`, never inline in a
  component or page.
- Every field must be populated — no `undefined` gaps that silently break
  rendering — but the *values* are honest placeholders, not real numbers.
- Real-world reference data (institution names, service URLs) may be real;
  amounts, dates, and statuses derived from them may not be invented.
- Components import mock data by name; they never construct their own.

## UI Rules

- Mobile-first, responsive with standard Tailwind breakpoints
  (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`), matching existing sections.
- Reuse `components/ui/*` primitives (Card, Badge, Button, Separator, ...) —
  never introduce a competing card/button implementation.
- Icons: `lucide-react` only. Animation: `motion/react` only. No emoji in
  rendered UI even if a ticket's mockup uses them as shorthand for an icon.
- No new dependencies without an explicit task requirement.
- Placeholder/demo content must visibly say so (a "Demo Data" badge or
  equivalent) — never presented as if it were live.

## Build Rules

- Build from `apps/marcos-dashboard/`: `npm run build` (runs `tsc -b` then
  `vite build`). Both must pass — a `tsc` error is a build failure.
- Lint via `npm run lint` (oxlint) when a task calls for it; not required for
  every change.
- Never loosen `tsconfig` strictness or add `// @ts-ignore` to force a build.

## Verification Rules

- A successful `npm run build` is necessary but not sufficient — confirm the
  feature's actual strings/behavior exist, e.g. `grep` the built
  `dist/assets/index-*.js` for expected text, or start `vite` on a scratch
  port and `curl` the route for a 200.
- Headless-browser screenshots are not available in this environment
  (missing system libraries) — bundle-grep and curl are the standard
  fallback verification method; do not skip verification because of this.
- Always stop any temporary dev server you started for verification.

## Definition of Done

A feature is done when, and only when:

- `npm run build` succeeds.
- The specific acceptance criteria in the task are verified, not assumed.
- No unrelated files were rewritten and no scope was added beyond the task.
- `PROJECT_STATE.md` is updated (Completed This Sprint, Current Task, Next
  Action) when the task instructs it.

## Token Efficiency Rules

- Read only the files a task requires — never scan the repository.
- Don't re-read a file immediately after writing or editing it; the tool
  result already confirms the change.
- Batch independent reads in a single parallel step instead of sequentially.
- Keep output to exactly what the task's Output Format asks for — no extra
  narration, no restated ticket text.
