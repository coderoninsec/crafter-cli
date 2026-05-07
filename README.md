# Crafter CLI

Crafter is a guided educational platform for learning how to build AI agents
progressively through stages.

It is not a generic framework, not an SDK, and not a benchmark tool. The
project is designed to feel like an interactive mentor: create a starter agent,
inspect the learning ladder, implement the next capability, and keep moving
forward.

## Philosophy

- CLI-first experience
- Progressive learning through stages
- Clear feedback over clever abstraction
- Small modules with obvious responsibilities
- Educational code that explains architecture

See [`codex.md`](codex.md) for the product and architecture philosophy that
guides the repository.

## Installation

Install directly from GitHub with `pipx`:

```bash
pipx install git+https://github.com/coderoninsec/crafter-cli.git
```

For local development, install the package in editable mode:

```bash
pip install -e .
```

## Quick Start

Create a starter learning project:

```bash
crafter create agent my-agent
```

Inspect the stage ladder:

```bash
crafter stages
```

Check the current hint:

```bash
crafter hint --path ./my-agent
```

See the next learning objective:

```bash
crafter next --path ./my-agent
```

Validate the project structure:

```bash
crafter doctor --path ./my-agent
```

Run the evaluator:

```bash
crafter test --path ./my-agent
```

## How the learning loop works

Crafter is intentionally sequential.

1. The scaffold starts incomplete but executable.
1. The evaluator checks the agent against staged capabilities.
1. The CLI reports what passed, what failed, and what unlocks next.
1. The learner improves one capability at a time.

The stage ladder currently teaches:

- introduction
- local setup
- first output
- connect LLM
- tools
- tool execution
- agent loop
- write tool
- your first agent

That progression is deliberate. It teaches agent design as a learning path, not
as a set of isolated test failures.

## Repository layout

- `crafter/cli.py` coordinates commands only
- `crafter/evaluator/` contains diagnostics and stage evaluation
- `crafter/stages/` defines the educational progression
- `crafter/core/` holds shared terminal rendering helpers
- `crafter/scaffold.py` generates starter projects
- `crafter/doctor.py` validates project structure and environment

## Commands

- `crafter create agent <name>`: generate a starter project
- `crafter stages`: list the full learning ladder
- `crafter hint --path <project>`: show the current hint
- `crafter next --path <project>`: show the next objective
- `crafter doctor --path <project>`: validate the project setup
- `crafter test --path <project>`: evaluate the agent and fail on missing capabilities
- `crafter status --path <project>`: evaluate the agent without failing the process
- `crafter explain <stage>`: explain one stage in mentor-friendly terms

`crafter stages` renders the academy as a visual roadmap instead of a technical
table, so the terminal feels closer to an interactive learning path.

## Extending Crafter

Keep future changes aligned with the current shape of the project:

- add new stage metadata in `crafter/stages/definitions.py`
- add new diagnostics in `crafter/evaluator/diagnostics.py`
- keep the CLI thin and route rendering through `crafter/core/`
- preserve the educational tone of the output
- prefer standard library code unless a dependency clearly improves the learner experience

If a future feature does not help a learner progress, explain a stage, or
improve the terminal mentoring experience, it probably does not belong here.
