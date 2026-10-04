# Vaultwarden Backup, Restore, Recovery & Rotation

Status: specification only — no backup job, cron entry, or offsite sync has
been created or run. See `VAULTWARDEN_ARCHITECTURE.md` for the deployment
this depends on (also not yet started).

## 1. What Must Be Backed Up

Per the upstream project's own backup guidance (verified 2026-10-04,
[Backing up your vault](https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-vault)),
a recoverable set is:

| Item | Path (inside the bind-mounted data dir) | Why it's required |
|---|---|---|
| `db.sqlite3` | `./vaultwarden-data/db.sqlite3` | Vault records, users, orgs. |
| `rsa_key*` files | `./vaultwarden-data/rsa_key*` | Signs active-session JWTs — without these, all logged-in sessions invalidate (not data loss, but an avoidable disruption). |
| `attachments/` | `./vaultwarden-data/attachments/` | File attachments — not stored in the DB. |
| `sends/` | `./vaultwarden-data/sends/` | Send feature's stored files. |
| `config.json` | `./vaultwarden-data/config.json` | Settings made via the admin panel (as opposed to env vars). |

**Critical correctness rule (verified, not assumed):** never raw-copy a live
`db.sqlite3` — the `-wal`/`-shm` sidecar files make a plain `cp` inconsistent.
Use SQLite's own backup API:

```bash
sqlite3 ./vaultwarden-data/db.sqlite3 ".backup '/tmp/vaultwarden-backup/db.sqlite3'"
```

## 2. Backup Architecture

```
LIVE INSTANCE (vaultwarden-data/, on the Builder VM)
    │  sqlite3 .backup (consistent snapshot, not a raw copy)
    ▼
LOCAL ENCRYPTED BACKUP
    - tar the snapshot + rsa_key* + attachments/ + sends/ + config.json
    - encrypt the tarball (age or gpg — age recommended: simpler key
      management, modern primitives) with a key held only in the physical
      emergency kit (§4), not on the Builder VM itself
    - retention: keep N most recent (e.g. 14 daily + 6 monthly) — exact N
      is an operational choice Marcos can tune, not an architectural one
    ▼
ENCRYPTED OFFSITE BACKUP
    - sync the already-encrypted local tarball to an offsite target
      (choice of target — e.g. a second physical location, or a cloud
      object store — is explicitly deferred to Marcos: it's a cost/
      convenience tradeoff, not a security one, since the blob is already
      encrypted before it leaves the Builder VM)
    ▼
RESTORE TESTING (§3)
```

Nothing here is wired to run automatically yet — this is the design a
future repository-level task (scheduled backup script + systemd timer or
cron, offsite sync target, restore-test automation) implements, each still
subject to the same "infrastructure change" approval gate as starting the
container itself.

## 3. Restore Testing

Per the mission brief: **a backup that has never successfully restored is
not considered validated.** Procedure:

1. Spin up a second, throwaway Vaultwarden container (ephemeral — same
   pattern TASK-0003 used for Postgres validation: stood up, tested, torn
   down, never the persistent named service) pointed at a scratch data dir.
2. Decrypt the backup tarball into that scratch dir.
3. Start the throwaway container, log in with a known test account's
   credentials, confirm: vault items present, an attachment downloads
   correctly, a Send still resolves, admin-panel settings from `config.json`
   took effect.
4. Tear down the throwaway container and scratch dir. Record the test date
   and result (pass/fail + what was checked) — this record is what makes a
   backup "validated" rather than merely "taken."
5. Repeat on a defined cadence (e.g. after every backup-system change, and
   periodically regardless — exact cadence is Marcos's call).

## 4. Physical Emergency Kit

A printed (or otherwise offline, non-cloud-synced) document, stored
somewhere physically secure and separate from the Builder VM itself (so a
single-location disaster doesn't take out both the live instance and the
only recovery path). **This repository never contains real values for any
of the placeholders below — only the template.**

```
VAULTWARDEN EMERGENCY RECOVERY KIT
Prepared: <date>          Last verified against live system: <date>

1. VAULT ACCESS
   Vault URL (DOMAIN):        ______________________________
   Account email:             ______________________________
   Master passphrase:        [not written here — see note below]
   2FA recovery code:         ______________________________

2. HARDWARE SECURITY KEYS
   Primary key (daily carry): make/model ____________________
   Spare key (stored with this kit): make/model ______________
   WebAuthn re-registration procedure if both keys are lost:
   ______________________________

3. BACKUP DECRYPTION
   Backup encryption key location (age/gpg key — NOT the key itself
   written here; name the physical/digital location it's actually kept):
   ______________________________
   Offsite backup location:   ______________________________

4. SERVER RECOVERY
   Builder VM access path if Tailscale/Cloudflare Access is unreachable:
   ______________________________
   Docker Compose file: docker/docker-compose.vaultwarden.yml
   Restore procedure: see VAULTWARDEN_BACKUP_RECOVERY.md §3

5. ADMIN ACCESS
   Admin panel token recovery (the ADMIN_TOKEN hash is in docker/.env,
   not here — note only where docker/.env itself is backed up):
   ______________________________
```

**Note on the master passphrase specifically:** per the mission brief's own
"no actual secrets in Git" rule, the real passphrase itself should not even
go in a printed copy of *this* document if that copy is ever photographed/
scanned/stored digitally — the standard approach (recommended, not yet
decided by Marcos) is a sealed physical envelope referenced by this sheet
("passphrase: see sealed envelope in [specific physical location]"), or a
split via something like a two-part Shamir scheme if Marcos wants defense
against losing the one envelope. This is exactly the kind of genuinely-his
decision this mission is not supposed to make unilaterally.

## 5. Breach-Driven, Transactional Rotation Workflow

Per the mission brief's explicit requirement — reproduced here as the
binding design, not re-derived, since it was already fully specified:

```
GENERATE new credential
    → SAVE PENDING safely (new credential stored in Vaultwarden as a
      *new* item or a clearly-marked pending field — never overwriting the
      old one yet)
    → CHANGE the remote account's password using the new credential
    → VERIFY login succeeds with the new credential against the real
      remote service
    → COMMIT: only now does the new credential become "the" credential for
      that item
    → RETAIN the old credential temporarily (rollback information) in case
      VERIFY passes but the site silently reverts, or a second factor was
      missed
    → REMOVE the obsolete credential only after a second confirmed-good
      login with the new one
```

**Explicitly not automated by this mission:** no script in this repository
performs an actual remote password change against any real external
account. This workflow is documented so that whenever rotation tooling is
eventually built (a future, separately-approved task), it's built against
this sequence rather than a simpler "generate and overwrite" approach that
risks exactly the "changed the remote password, then lost the new one"
failure mode the mission brief calls out by name. AI may *identify* a
breach signal or *assist* drafting the new credential; it does not
autonomously execute a real rotation during or after this mission without
separate explicit authorization.
