# Skill: Context Builder

## Purpose
Generate `.context/current.md` — a single condensed, human-readable summary of project state — as a rendered view of `.engineering/context.json`, so routine commands can avoid re-reading `PROJECT_STATE.md`, `HANDOFF.md`, and `NEXT_TASK.md` in full on every invocation.

## Responsibilities
- Read `.engineering/context.json` as the primary source, resolving its `refs` (`repository.json`, `executives.json`, `workflows.json`, `commands.json`, `metrics.json`) as needed to fill in Architecture/Services detail.
- Produce a condensed summary covering exactly six sections: Current Sprint, Current Task, Current Architecture, Current Services, Outstanding Decisions, Next Action.
- Overwrite `.context/current.md` with the regenerated summary, including a "Last generated" footer citing `.engineering/context.json` as the source.
- Keep the summary short enough to be materially cheaper to read than the JSON+markdown it's built from — prose, not a raw JSON dump.
- When `.engineering/context.json` or any file it references is updated (e.g. by `documentation-engineer` at the end of a sprint), regenerate `.context/current.md` to match. JSON is the source of truth; the markdown file is always downstream of it.

## Inputs
- `.engineering/context.json` (primary)
- `.engineering/repository.json`, `.engineering/executives.json`, `.engineering/workflows.json`, `.engineering/commands.json`, `.engineering/metrics.json` (resolved via `context.json` refs, as needed)
- `PROJECT_STATE.md`, `HANDOFF.md`, `NEXT_TASK.md` — fallback only, if `.engineering/context.json` is missing or does not yet exist

## Outputs
- `.context/current.md`, fully overwritten (not appended)

## Success Criteria
- All six required sections are present and accurate as of `.engineering/context.json` at generation time.
- No fact in `.context/current.md` is hand-typed independently of the JSON — every line traces back to `.engineering/context.json` or a file it references.
- The generated file is meaningfully smaller than the JSON + markdown state it summarizes.

## Rules
- Never hand-edit `.context/current.md` — it is a generated output. Edit `.engineering/context.json` (or the file it references) and regenerate instead, so the two cannot drift apart.
- Never treat `.context/current.md` as authoritative for implementation-level detail (full acceptance criteria, full file lists, full architecture rationale) — it is a summary for orientation only. Commands doing real implementation work (`/feature`, `/bug`, `/review`, `/document`) still read the full source documents.
- Do not duplicate data across `.engineering/*.json` files — `context.json` stays small by referencing `repository.json`/`executives.json`/`workflows.json`/`commands.json`/`metrics.json` rather than inlining their contents.

## When NOT to Use
- When a task needs full acceptance criteria, full known-issues detail, or anything the six-section summary would truncate — read `.engineering/*.json` or the markdown source documents directly instead.
- Mid-sprint, before `.engineering/context.json` has actually changed — regenerating against an unchanged source wastes tokens for no benefit.
