---
name: voodoo-production-deployment
description: Prepare and review a Voodoo application for secure production deployment, including fail-closed configuration, health/readiness, secrets, proxy trust, package provenance, and rollback evidence.
---

# Voodoo Production Deployment

Use this skill when an application is moving from local development to a
controlled production environment.

## Required gates

1. Set `VOODOO_ENV=production` and provide a non-development signing secret.
2. Require secure cookies, CSRF, HSTS, explicit CORS origins, and validated
   proxy trust; never enable credentialed wildcard CORS.
3. Use the Runtime-owned Store path and one writer per Runtime process.
4. Expose `/healthz`, `/readyz`, `/status`, and bounded Prometheus metrics.
5. Verify backup, restore, upgrade, rollback, and clean-install evidence before
   accepting traffic.
6. Publish checksums, SBOM, provenance, and release-note evidence for the exact
   artifacts tested.

Prefer the repository production runbook and executable CI contracts over
hand-written deployment folklore. Record exceptions with an owner, expiry, and
rollback plan.
