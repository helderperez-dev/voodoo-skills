# Voodoo Skills

This repository distributes Agent Skills for the Voodoo ecosystem.

Rules for contributors and agents:

- Treat `helderperez-dev/voodoo` and `helderperez-dev/voodoo-store` as implementation sources of truth.
- Do not invent public Voodoo APIs. Verify current code before documenting a symbol.
- Keep `SKILL.md` files concise and link to supporting references.
- Preserve architectural distinctions: Runtime owns semantics/authority; Store owns durable mechanics.
- Prefer native Store primitives over compatibility KV encodings.
- Do not claim distributed guarantees that are not implemented and tested.
- When a public Voodoo API changes, update the corresponding skill in the same development cycle.
