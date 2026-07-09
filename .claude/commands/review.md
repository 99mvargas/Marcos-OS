---
description: Review the current diff for correctness bugs and security issues.
---

Use the `code-review` skill against the current diff.

1. Identify concrete correctness bugs with a specific failure scenario, and reuse/simplification/efficiency issues.
2. If the diff touches security-sensitive surface (integrations, credentials, secrets, high-risk actions per `VISION.md` Security Philosophy), also apply the `security-review` skill.
3. Rank findings most-severe first.
4. Do not apply fixes unless explicitly asked.

Report the ranked findings, or state that none survived verification.
