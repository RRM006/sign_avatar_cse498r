# 04 — Setup & Run

<!-- HOW TO USE THIS TEMPLATE
Give EXACT, copy-pasteable steps read from the project (README, scripts, manifests, CI config, infra).
Test the steps against what the code/config actually requires; don't invent commands.
Cover every OS/environment the project must support. Delete guidance comments before saving.
For env vars/keys: list every one the project needs, with a PLACEHOLDER value — NEVER a real secret. -->

## 1. Prerequisites

[[Required runtimes/tools and versions (language runtime, package manager, DB, system packages,
accounts/services). Note anything OS-specific. Cite where you found each requirement.]]

## 2. Install

```
[[exact install commands — environment setup, dependency install, any bootstrapping.
Include per-OS variants if the project supports more than one.]]
```

## 3. Configure (environment variables / secrets)

<!-- List EVERY env var / key / config value the project reads. Placeholder values only. Say which
are required vs optional, and what each does. Point to the real config file/mechanism. -->

| Variable | Purpose | Placeholder / default |
|---|---|---|
| [[NAME]] | [[what it's for]] | [[<placeholder> or default]] |
| [[NAME]] | [[...]] | [[...]] |

[[How config is loaded (env file? secrets manager? CLI flags?), and any "restart required after
changing X" gotchas. Cite the source. NEVER include a real secret value.]]

## 4. Run locally

```
[[exact command(s) to start the app / service / tool, including host/port and how to open it.
Include how to run in dev/watch mode vs. normal, if applicable.]]
```

[[Any important run-time notes: seed data, first-run migrations, default login/credentials for a
dev environment, common startup gotchas.]]

## 5. Run the tests

```
[[exact test command(s)]]
```

[[What passing looks like (expected count/output if known), any test-only setup (env, fixtures,
encoding flags), and how long they take / whether they need network.]]

## 6. Build / deploy

[[Build command(s) and artifacts, if any. Deployment steps or target(s). If deployment isn't set up
yet, say exactly that and note what exists (e.g. a local run command only). Cite sources.]]

## 7. Other operational notes

[[Anything else a newcomer needs to actually run it: key rotation, data reset, external service
setup, hardware/OS constraints, optional components and how to enable them. Omit if none.]]
