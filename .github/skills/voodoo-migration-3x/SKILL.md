---
name: voodoo-migration-3x
description: Migrate a Voodoo 2.x or legacy adapter application to the 3.x Runtime/Store architecture with compatibility checks, durable-record safety, and rollback planning.
---

# Voodoo 3.x Migration

Treat migration as an evidence-driven compatibility change, not a global
search-and-replace.

1. Inventory imports, adapters, hidden databases, background workers, and
   generated scaffolds before changing code.
2. Move semantics to the canonical Runtime and durable mechanics to the one
   Store writer; retain legacy adapters only at explicit boundaries.
3. Version every durable record and test legacy reads, current writes, future
   rejection, restart, backup, and rollback.
4. Replace `voodoo create` with `voodoo new`; update docs and generated apps.
5. Run the compatibility matrix and keep a reversible deployment migration
   with a verified backup before promotion.

Do not silently reinterpret an old record or delete a compatibility path until
its documented removal window and migration evidence are complete.
