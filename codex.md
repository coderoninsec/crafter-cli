# Crafter Philosophy

Crafter is not a generic AI framework.

It is a guided educational platform for learning how to build AI agents progressively through stages.

Every feature must support:

* learning
* progression
* mentorship
* CLI-first UX

---

# Product Identity

Crafter should feel like:

* Hack The Box
* CodeCrafters
* an interactive mentor

Crafter should NOT feel like:

* a benchmark tool
* a linter
* a static validator

---

# Educational Principles

* Agents should start incomplete but executable
* Stages must unlock sequentially
* Hints should guide, not solve
* Errors should educate
* Stages represent learning milestones, not technical tests

---

# Architecture Rules

* CLI layer must remain thin
* Stage logic belongs in `stages/`
* Evaluation logic belongs in `evaluator/`
* Educational metadata belongs in `definitions.py`
* Do not duplicate evaluation logic

---

# Code Style Rules

* Prefer the Python standard library
* Keep modules small and focused
* Add educational comments
* Avoid magic abstractions
* Prefer explicit educational logic over clever architecture

---

# UX Rules

* CLI output should feel motivating and progression-oriented
* Feedback should explain:

  * what failed
  * why it matters
  * how to improve
* The terminal experience should feel interactive and guided

---

# Stage Requirements

Every stage must contain:

* title
* description
* hint
* explanation
* why_it_matters
* implementation_example
* common_mistake

---

# Scaffold Rules

Generated agents must:

* start incomplete
* remain executable
* fail progressively
* encourage learning through implementation

The scaffold is a training lab, not a completed template.
