# VISION

This is the permanent constitutional vision for Marcos OS. It defines what
Marcos OS is trying to become — not the roadmap, not a backlog, not
marketing, not implementation detail. Those live in `ROADMAP.md`, `TODO.md`,
and `DEVELOPMENT.md` respectively.

# Mission

Marcos OS exists to help Marcos make better decisions, faster, across every
area of his life and business.

# Core Purpose

Marcos carries the mental load of running his finances, his business, his
home infrastructure, his health, and his relationships largely alone. Marcos
OS exists to carry that load with him — not by replacing his judgment, but by
organizing the information, surfacing what matters, and recommending the
highest-leverage next action in each area of his life. It exists to help him
make better decisions, not to make decisions for him.

# Core Principles

- Decision-first, not data-first. A dashboard full of numbers is not the
  goal; a clear recommendation is.
- Every Executive exists to recommend actions, not merely to display state.
- Recommendations must explain why. An action without a reason is not
  trustworthy and will not be acted on.
- Optimize for long-term ROI over short-term completeness. Depth in one
  domain beats shallow coverage of many.
- Protect privacy and security as a default, not an afterthought.
- The human remains in control. Marcos OS advises; Marcos decides.
- AI advises, and never acts autonomously on high-risk decisions — financial
  transfers, irreversible changes, and anything with real-world consequence
  always require explicit human approval.

# Executive Architecture

Marcos OS is composed of independent Executives — one per domain of Marcos's
life. Each Executive is a self-contained unit of responsibility, not a page
or a feature.

Current Executives:

- Home
- Finance
- Infrastructure

Planned Executives:

- Business
- Purchasing
- Knowledge
- Health
- Identity

Each Executive owns:

- Its own data — the facts and records relevant to its domain.
- Its own integrations — how it connects to the outside world.
- Its own analysis — how it interprets its data.
- Its own recommendations — the actions it believes Marcos should take.
- Its own actions — the operations it can carry out, always subject to the
  human-control and high-risk-approval principles above.

Executives do not reach into one another's data. They are independent so
that any one of them can grow in depth without destabilizing the others.

# Shared Engines

Executives are independent, but they share a small set of platform
components that give Marcos OS its coherence:

- **Timeline Engine** — the single chronological thread of what happened,
  across every Executive, so Marcos never has to reconstruct "what led to
  this" from memory.
- **Recommendation Engine** — the shared mechanism by which any Executive's
  analysis becomes a ranked, explained recommendation Marcos actually sees.
- **Decision Engine** — the record of decisions Marcos has made or is being
  asked to make, so nothing is silently re-litigated or silently dropped.
- **Memory Engine** — the durable record of what is true about Marcos's
  life and work, so no Executive or session has to rediscover it.
- **Integration Framework** — the shared seam through which Executives
  connect to external systems and data sources, so each Executive doesn't
  reinvent how it talks to the outside world.
- **Goal Engine** — the mechanism for tracking what Marcos is working toward
  in any domain, and whether today's actions move him closer or further away.

Together, these engines are what make Marcos OS a system rather than a
collection of unrelated tools.

# Security Philosophy

- Default to least privilege in every integration and every access grant.
- Prefer local-first when practical, minimizing what leaves Marcos's own
  infrastructure.
- Prefer read-only integrations wherever a read-only mode achieves the goal.
- Never store bank credentials directly; rely on token-based, revocable
  access instead.
- Secrets remain server-side, never embedded in client-facing code.
- Encrypt sensitive data, both in transit and at rest.
- Require human approval before any high-risk action is taken on Marcos's
  behalf.

# Long-Term Vision

Marcos OS is an Executive Operating System: a standing set of domain
Executives, backed by shared engines, that continuously helps Marcos
improve his:

- Finances
- Business
- Infrastructure
- Knowledge
- Purchasing
- Health

Its success is not measured by how many dashboards or features it has. It is
measured by whether Marcos is making better decisions, more consistently,
with less mental overhead, than he would without it.
