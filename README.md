# Voodoo Skills

Official Agent Skills for the **Voodoo ecosystem**.

This repository packages reusable development guidance for AI coding agents so they understand how to build with Voodoo, evolve Voodoo Framework, and work on Voodoo Store without rediscovering the architecture or falling back to generic framework patterns.

## Included skills

### `voodoo-development`

For application development with Voodoo:

- Model and UUIDv7 identity
- `field()`, indexes, unique constraints and defaults
- typed relationships
- validation
- Runtime vs Store ownership
- Jobs, Events, Streams, Topics and Objects
- agents and autonomous systems
- Voodoo application anti-patterns

### `voodoo-core-development`

For contributors changing Voodoo Framework itself:

- canonical execution lifecycle
- Runtime authority
- Store ownership
- adapter design
- Store Python binding boundary
- framework CI and release gates
- architectural invariants

### `voodoo-store-development`

For development of Voodoo Store:

- Rust core
- native Store primitives
- cross-domain transactions
- PyO3 Python binding
- Python API design
- Store packaging and releases

## Use today with VS Code / GitHub Copilot

Clone the repository:

```bash
git clone git@github.com:helderperez-dev/voodoo-skills.git
cd voodoo-skills
```

### Install globally for Copilot

macOS / Linux:

```bash
bash scripts/install.sh copilot
```

This installs into:

```text
~/.copilot/skills/
├── voodoo-development/
├── voodoo-core-development/
└── voodoo-store-development/
```

Reload VS Code after the first installation if necessary.

### Install into one project only

For example, inside the Voodoo Framework checkout:

```bash
bash scripts/install.sh project ~/code/voodoo
```

The skills are copied to:

```text
<project>/.github/skills/
```

### Generic agent location

For agents that discover skills from `~/.agents/skills`:

```bash
bash scripts/install.sh agents
```

### Windows / PowerShell

Global Copilot installation:

```powershell
.\scripts\install.ps1 -Target copilot
```

Project installation:

```powershell
.\scripts\install.ps1 -Target project -ProjectPath C:\code\voodoo
```

## Using the skills

A skills-capable agent may discover a skill automatically from its description.

You can also explicitly tell the coding agent which Voodoo skill to use.

Examples:

```text
Use the voodoo-development skill and build a Customer model with indexed email lookup.
```

```text
Use voodoo-core-development. Review this change and make sure it preserves Runtime ownership of Store.
```

```text
Use voodoo-store-development. Expose this new Rust primitive through the Python binding.
```

When the client exposes slash-command style skill invocation, the corresponding names are:

```text
/voodoo-development
/voodoo-core-development
/voodoo-store-development
```

## Repository layout

```text
voodoo-skills/
├── .github/
│   └── skills/
│       ├── voodoo-development/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── voodoo-core-development/
│       │   ├── SKILL.md
│       │   └── references/
│       └── voodoo-store-development/
│           ├── SKILL.md
│           └── references/
├── scripts/
│   ├── install.sh
│   └── install.ps1
├── AGENTS.md
└── README.md
```

## Source-of-truth strategy

This repository is the **distribution repository**.

The intended long-term ownership model is:

```text
helderperez-dev/voodoo
  ├── voodoo-development
  └── voodoo-core-development

helderperez-dev/voodoo-store
  └── voodoo-store-development

             ↓ sync/release

helderperez-dev/voodoo-skills
  └── distribution for coding agents
```

This keeps architectural guidance versioned near the implementation while providing one convenient installation repository.

## Core philosophy

> Do not implement a generic industry pattern merely because it is familiar. First determine whether Voodoo already has a native primitive or architectural rule for the problem.

The primary architectural rules are:

1. Runtime owns semantics and authority.
2. Store owns durable mechanics.
3. AI is Compute, not a second Runtime.
4. Effect != Observation.
5. Prefer local-first mechanics.
6. One Runtime process owns one Store writer.
7. Prefer native Store primitives over compatibility encodings.
8. Python typing expresses data semantics.
9. `field()` expresses persistence metadata.
10. `relation()` expresses relationships and lifecycle policy.
11. Do not claim distributed guarantees that Voodoo does not implement and test.
12. Add operational complexity only when a real product requirement demands it.

## Updating

After pulling a newer version of this repository, reinstall:

```bash
git pull
bash scripts/install.sh copilot
```

The installer replaces only the three Voodoo skill directories it owns.
