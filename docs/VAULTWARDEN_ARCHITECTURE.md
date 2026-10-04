# Vaultwarden Architecture & Security Spec

Status: **specification only — nothing in this document has been deployed,
started, or exposed.** Per `docs/AUTONOMOUS_AGENT_PROTOCOL.md` §10, starting
the container, creating a Cloudflare Tunnel hostname, or changing any
network/DNS/firewall configuration are each `HUMAN APPROVAL` actions and are
explicitly called out as not-yet-authorized below, not performed.

Sources for every setting referenced here are the upstream project's own
docs, verified 2026-10-04 (not assumed from memory):
[Vaultwarden Admin page/token wiki](https://github.com/dani-garcia/vaultwarden/wiki/Enabling-admin-page),
[Vaultwarden backup wiki](https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-vault),
current stable release [1.37.x](https://github.com/dani-garcia/vaultwarden/releases).

## 1. Objectives (from the mission brief)

Security + recoverability + convenience, simultaneously:

- Unique strong random credentials per site, generated and stored in-vault.
- Strong memorable master passphrase (Diceware-style, not reused anywhere
  else) — this is the one secret Marcos must memorize; everything else is
  random and vault-stored.
- Passkeys (FIDO2/WebAuthn) wherever the target site supports them —
  Vaultwarden's own vault items support storing/filling passkeys; this is a
  per-site adoption effort, not a server setting.
- FIDO2/WebAuthn as a *login* factor for the vault itself, eventually two
  hardware keys (one daily-carry, one stored with the recovery kit as a
  spare) registered as WebAuthn credentials on the Vaultwarden account.
- Household sharing via a Vaultwarden Organization (shared collections),
  not shared master passwords.
- Encrypted local + offsite backups, with restore testing (see
  `VAULTWARDEN_BACKUP_RECOVERY.md`).
- No arbitrary time-based rotation; rotation only on breach/compromise
  signal, and only via the transactional workflow the mission brief already
  specified (see `VAULTWARDEN_BACKUP_RECOVERY.md` §3).

## 2. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Builder VM (existing Docker host)                        │
│                                                           │
│  vaultwarden container (vaultwarden/server:1.37.1-alpine)│
│   - SQLite backend (default; no separate DB service —    │
│     a single-household instance has no scale reason to   │
│     add Postgres here, matching docs/RUNTIME_ARCHITECTURE │
│     .md §23's "don't add infra without a measurable       │
│     requirement" precedent)                               │
│   - bind-mounted data dir (./vaultwarden-data:/data)      │
│   - bound to 127.0.0.1 only, like marcos-tasks-db         │
│     (docker-compose.marcos-os.yml) — no inbound port on   │
│     the LAN/WAN by default                                │
└─────────────────────────────────────────────────────────┘
        │ localhost only — no path in from outside the VM yet
        ▼
   (reverse-proxy / tunnel layer — §4, NOT YET CONFIGURED)
```

Deployment file (new, not started): `docker/docker-compose.vaultwarden.yml`.
Follows this repo's existing per-service compose file convention
(`docker-compose.jellyfin.yml`, `docker-compose.portainer.yml`), not folded
into `docker-compose.marcos-os.yml` — Vaultwarden is unrelated to the
Autonomous Agent Protocol runtime store that file already documents.

## 3. Hardening Settings

All of the following are real, documented Vaultwarden environment variables
(verified against the project wiki, not invented); none are set to a live
value here — `docker/.env.example` documents names only, same pattern as
`MARCOS_TASKS_DB_PASSWORD` in TASK-0003.

| Setting | Value | Why |
|---|---|---|
| `SIGNUPS_ALLOWED` | `false` **after** the household's accounts are created once | Prevents any internet-reachable instance (even behind the tunnel layer in §4) from accepting a stranger's signup. Verified default is `true`; must be explicitly disabled post-setup. |
| `ADMIN_TOKEN` | An Argon2id PHC hash (`vaultwarden hash` or `openssl` + the project's documented hashing command), not a plaintext token | Vaultwarden documents both plaintext and Argon2id-hash forms; the hash form means the admin panel password isn't recoverable from the env file/compose config itself if that file ever leaks. |
| `WEBSOCKET_ENABLED` | `true` | Needed for real-time sync across devices; requires the reverse-proxy layer to forward the `Upgrade`/`Connection` headers (see §4). |
| `DOMAIN` | `https://<chosen hostname>` | Used to build invite/reset-link URLs and the websocket URL — must match whatever hostname §4 settles on, or links in emails break. |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_SECURITY=starttls` / `SMTP_FROM` / `SMTP_USERNAME` / `SMTP_PASSWORD` | Household's existing mail provider | Required for email verification, invites, and password-reset flow — without SMTP configured, those flows silently fail. |
| Image tag | `vaultwarden/server:1.37.1-alpine` (pinned, Alpine variant) | Current stable per upstream releases; pinned (not `:latest`) per the mission brief's version-pinning requirement — `docker-compose.jellyfin.yml`'s `:latest` is pre-existing drift in this repo, not a pattern to repeat here. |

Not yet decided (needs Marcos, not purely a repository-level call — see §5):
the actual `DOMAIN` hostname, and whether household member accounts are
created by Marcos directly in the admin panel (invite-only, `SIGNUPS_ALLOWED`
never flipped `true` at all) or briefly allowed to self-register once before
disabling signups.

## 4. Network / Remote Access

**Constraint already on record:** Covenant Eyes on Marcos's iPhone has
previously conflicted with Tailscale. A Tailscale-only design is therefore
not assumed reliable for the one device (iPhone + official Bitwarden app)
that most needs always-available access. iOS generally allows only one
active VPN/Network Extension profile at a time, so this isn't specific to
Tailscale — any VPN-based path (Tailscale, WireGuard, UniFi's own VPN
server) risks the same class of conflict on that device unless Covenant
Eyes' current version is re-verified to coexist with a specific VPN client,
which has not been done here.

**Recommendation (spec only, not implemented):**

- **Mobile (iPhone) and any network the household might be on:** Cloudflare
  Tunnel (already present in this environment per the mission brief) to a
  dedicated hostname (e.g. `vault.<domain>`), gated by **Cloudflare Access**
  (Zero Trust) in front of the tunnel — an email-OTP or hardware-key-backed
  Access policy restricted to the household's specific email addresses, not
  an open public endpoint. This needs no VPN client running on the iPhone at
  all, so it cannot conflict with Covenant Eyes. The official Bitwarden iOS
  app talks plain HTTPS to the `DOMAIN` — Access sits in front of that.
- **Desktop/laptop/browser extension (devices that don't run Covenant Eyes):**
  Tailscale directly to the Builder VM is simpler and already available, and
  remains a fine option for those devices specifically — no reason to force
  everything through Cloudflare Access if a given device has no conflict.
- Either path keeps the Vaultwarden container itself bound to
  `127.0.0.1`-only (§2) — nothing changes in UniFi UXG-Max port-forwarding,
  no inbound WAN port is opened directly to the container.

**Explicitly not done by this spec (per the mission brief's own
constraint and `AUTONOMOUS_AGENT_PROTOCOL.md` §10):** creating the Cloudflare
Tunnel hostname, writing the Access policy, or touching any DNS/firewall
config. That is a live Cloudflare/network change — recorded as
**HUMAN_REQUIRED** (see the task's `human_action` once a `tasks/TASK-00XX-
vaultwarden-deployment.yaml` is opened): reason `ARCHITECTURE_DECISION` +
`INFRASTRUCTURE_CHANGE`, risk `MEDIUM` (new public-adjacent surface, though
Access-gated), action required: Marcos picks the hostname and confirms the
Cloudflare Access policy scope (which emails/devices) before anything is
created.

## 5. Open Decisions for Marcos (not architectural — genuinely his to make)

1. Hostname for `DOMAIN` (subdomain choice).
2. Cloudflare Access policy membership (which household emails).
3. Invite-only account creation vs. one-time self-registration window.
4. Which two physical FIDO2/WebAuthn keys to buy (brand/model) — a
   repository-level task can document *how* to register them once chosen,
   not which ones to buy.

## 6. Explicitly Rejected / Deferred

- **Running Vaultwarden on Postgres instead of SQLite.** Vaultwarden
  supports both; SQLite is the documented default and sufficient for a
  single-household instance with no measurable scale requirement — adding a
  second Postgres service here (distinct from TASK-0003's unrelated
  `marcos-tasks-db`) would be unjustified complexity, same reasoning
  `docs/RUNTIME_ARCHITECTURE.md` §23 already applied to this repo's runtime
  store.
- **Public exposure with no Access layer.** Rejected outright per the
  mission brief's explicit constraint.
- **Time-based credential rotation (30/60/90 day).** Rejected per the
  mission brief; see `VAULTWARDEN_BACKUP_RECOVERY.md` §3 for the
  breach-driven, transactional alternative.
