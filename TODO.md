# TODO — Highest ROI Work Queue

Not a backlog. Sorted by expected ROI, highest first. Pull the top item that
isn't Blocked.

| # | Task | Priority | Expected ROI | Dependencies | Complexity | Status |
|---|---|---|---|---|---|---|
| 1 | Statement Parser | P0 | Critical — unlocks Budget, Timeline, Recommendation, and Goal Engines | Statement Vault v1 (done) | S | Queued — spec ready in `NEXT_TASK.md` |
| 2 | Infrastructure Executive | P0 | High — resolves known nav issue (currently routes to `/`); gives Infrastructure its own page | None — Infrastructure section + Service Registry already exist | S | Not started |
| 3 | Budget Engine | P1 | High — core Finance Executive value (category budgets, overspend detection) | Statement Parser | M | Blocked — waiting on Statement Parser |
| 4 | Knowledge Executive | P1 | Medium-High — real data source already exists (`obsidian/` vault), low integration risk | None | M | Not started |
| 5 | Timeline Engine | P1 | Medium-High — unifies Finance + Infrastructure events into one chronological view | Statement Parser, Infrastructure Executive | M | Blocked — waiting on Statement Parser, Infrastructure Executive |
| 6 | Recommendation Engine | P2 | Medium — replaces the hardcoded "Highest ROI Today" mock with a real cross-executive engine | Budget Engine, Infrastructure Executive | L | Blocked — waiting on Budget Engine, Infrastructure Executive |
| 7 | Goal Engine | P2 | Medium — debt-free date and savings goal tracking off real numbers | Budget Engine | M | Blocked — waiting on Budget Engine |
| 8 | Identity Executive | P2 | Medium — real source exists (`obsidian/Identity/Identity.md`); likely a weighting input for Recommendation Engine | Architecture decision needed — not part of the current 7-item Executives nav | M | Not started — needs Chief Systems Architect decision |
| 9 | Decision Engine | P3 | Low-Medium — formalizes the "Decisions Awaiting Approval" workflow | Recommendation Engine | M | Blocked — waiting on Recommendation Engine |
| 10 | Business Executive | P3 | Low-Medium — new domain, no foundation or data source yet | None | M | Not started |
| 11 | Purchasing Executive | P3 | Low — no purchase-data source until a Finance provider exists | Plaid Adapter v1 (not started) | M | Blocked — waiting on Plaid Adapter v1 |
| 12 | Habit Engine | P3 | Low — no domain foundation to attach habits to yet | Health Executive | M | Blocked — waiting on Health Executive |
| 13 | Health Executive | P3 | Low — no data source/provider identified yet | Architecture decision needed — data source undefined | L | Not started — needs Chief Systems Architect decision |
