---
name: voodoo-store-backup-recovery
description: Operate Voodoo Store backups, verification, corruption recovery, compaction, quotas, and disaster-recovery drills safely.
---

# Voodoo Store Backup and Recovery

Backups are evidence-bearing artifacts, not opaque copies.

- Run verification and retain the format/version/checksum manifest.
- Keep the source Store closed or use the documented consistent backup path.
- Test restore into a fresh path, reopen it, and compare committed logical
  state before promotion.
- Treat corruption, torn tails, disk-full, quota, and lock contention as
  actionable typed failure modes; do not delete the source during repair.
- Run compaction to a distinct destination, verify it, then use an explicit
  atomic replacement/rollback procedure.
- Record recovery records, commit errors, queue lag, object I/O, compaction
  backlog, and lock contention in the operational evidence.

Use the Store game-day and retained legacy-fixture workflows before claiming
restore certification.
