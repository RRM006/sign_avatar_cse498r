# 02 — Architecture & Stack

<!-- HOW TO USE THIS TEMPLATE
Fill from what you actually read in the project (dependency files, config, source, infra files).
Delete guidance comments before saving. Mark inferences "(inferred)". Unknowns go in 07. -->

## Full tech stack

<!-- Build a table of every meaningful technology: languages, runtimes, frameworks, key libraries,
databases, external services/APIs, build tools, hosting/deploy. Include versions where pinned
(read them from lockfiles / manifests, don't guess). Add a "Notes" column for anything important
(e.g. "planned but not installed", "swappable behind an interface", "dev-only"). -->

| Layer | Choice | Notes |
|---|---|---|
| Language(s) | [[...]] | [[...]] |
| Framework(s) | [[...]] | [[...]] |
| Database / storage | [[...]] | [[...]] |
| Key libraries | [[...]] | [[...]] |
| External services / APIs | [[...]] | [[...]] |
| Build / tooling | [[...]] | [[...]] |
| Tests | [[...]] | [[...]] |
| Hosting / deployment | [[...]] | [[...]] |

[[If the project has a notable cross-cutting strategy — e.g. how it chooses between providers, how it
handles config/secrets, a plugin/seam pattern — summarize it here and cite the file.]]

## Folder & file map

<!-- A tree of the repo with a ONE-LINE description of each KEY folder/file — enough that a newcomer
knows where to look, not an exhaustive listing. Prioritize entry points, config, the core domain
logic, and anything non-obvious. If the project's own docs describe a "planned" structure that
differs from what's actually on disk, note the difference and mark planned-but-absent items. -->

```
[[project-root]]/
├── [[path]]            # [[one-line description]]
├── [[path]]            # [[one-line description]]
│   └── [[path]]        # [[one-line description]]
└── [[path]]            # [[one-line description]]
```

## How data / requests flow through the system

<!-- Describe the main flow(s) end to end: the primary user journey and/or request lifecycle, and
any background/async work. A simple text or ASCII diagram is ideal. Name the actual modules/files/
endpoints involved so a newcomer can trace it in code. Include the data model backbone (main
entities/tables and how they relate) if the project has one. -->

[[Primary flow — step by step, naming the real components at each step.]]

[[Secondary flows (admin/staff side, background jobs, integrations) if any.]]

[[Data model / storage backbone: the main entities and key relationships; where the schema lives;
how schema changes are managed (migrations?). Cite the source.]]

[[Entry points actually exposed (URLs, CLI commands, ports, public functions) — read from the code.]]
