"""Academy stage definitions for Crafter.

The academy is the source of truth. This module defines the official learning
path exactly once so the CLI, evaluator, and future UX layers can all stay in
sync without duplicating progression rules.
"""

from __future__ import annotations

from typing import Any


# The academy is the source of truth. Stage order, labels, and learning goals
# are defined here once so the evaluator and roadmap can stay synchronized.
STAGES: list[dict[str, Any]] = [
    {
        "id": 1,
        "slug": "introduction",
        "title": "Introduction",
        "description": "Understand the Crafter journey and learner contract.",
        "minutes": "5 min",
        "academy_order": 1,
        "check": None,
        "capability": "Understand the training path and the agent contract.",
        "hint": "Start by reading the scaffold and identifying the required Agent shape.",
        "explanation": "This opening stage orients the learner before any code changes. It explains what Crafter expects and how the progression will work.",
        "why_it_matters": "A clear start reduces confusion and makes every later milestone easier to understand.",
        "implementation_example": "Read the scaffold, open app/agent.py, and identify the Agent class contract.",
        "common_mistake": "Jumping into implementation before understanding the learning path and required entry point.",
        "example": "class Agent:\n    def run(self, input_text: str) -> dict:\n        return {\"output\": \"\", \"tools_used\": [], \"memory\": {}, \"error\": None}",
    },
    {
        "id": 2,
        "slug": "local-setup",
        "title": "Local Setup",
        "description": "Configure your local environment.",
        "minutes": "10 min",
        "academy_order": 2,
        "check": "project_structure",
        "capability": "Your local project is ready to run in the terminal.",
        "hint": "Make sure the scaffold is installed, the project root is valid, and Crafter can load the agent.",
        "explanation": "This stage is about preparing the workspace so the learner can move quickly through the rest of the academy without fighting setup issues.",
        "why_it_matters": "A smooth local setup makes the learning loop feel immediate instead of blocked by environment problems.",
        "implementation_example": "Create the scaffold, confirm app/agent.py exists, and verify the CLI can see the project.",
        "common_mistake": "Treating setup as a throwaway detail instead of part of the learning experience.",
        "example": "crafter create agent my-agent",
    },
    {
        "id": 3,
        "slug": "first-output",
        "title": "First Output",
        "description": "Return your first valid response.",
        "minutes": "6 min",
        "academy_order": 3,
        "check": "first_response",
        "capability": "Your agent produces a real response.",
        "hint": "Return any non-empty output from run().",
        "explanation": "This stage teaches the simplest meaningful agent behavior: accept input and return something useful instead of an empty placeholder.",
        "why_it_matters": "Every later stage depends on the agent having a reliable response path.",
        "implementation_example": "return {\"output\": \"hello\", \"tools_used\": [], \"memory\": {}, \"error\": None}",
        "common_mistake": "Returning an empty string, None, or a payload that is not a dictionary.",
        "example": "def run(self, input_text: str) -> dict:\n    return {\"output\": \"hello\", \"tools_used\": [], \"memory\": {}, \"error\": None}",
    },
    {
        "id": 4,
        "slug": "connect-llm",
        "title": "Connect LLM",
        "description": "Connect your first reasoning flow.",
        "minutes": "10-15 min",
        "academy_order": 4,
        "check": "llm_connection",
        "capability": "Your agent responds to a conversational prompt.",
        "hint": "Teach the agent to handle a prompt like ping and return a stable answer.",
        "explanation": "This stage introduces the first conversational connection pattern so the learner can see how input becomes a deliberate response.",
        "why_it_matters": "Once the agent can answer a simple prompt, it stops feeling like a stub and starts feeling interactive.",
        "implementation_example": "if input_text == \"ping\":\n    return {\"output\": \"pong\", \"tools_used\": [], \"memory\": {}, \"error\": None}",
        "common_mistake": "Hard-coding a response without matching the expected input flow.",
        "example": "if input_text == \"ping\":\n    return {\"output\": \"pong\", \"tools_used\": [], \"memory\": {}, \"error\": None}",
    },
    {
        "id": 5,
        "slug": "tools",
        "title": "Tools",
        "description": "Define your available tools.",
        "minutes": "10 min",
        "academy_order": 5,
        "check": "tool_definition",
        "capability": "Your agent exposes a tool registry.",
        "hint": "Add a clear tools collection to the agent.",
        "explanation": "This stage teaches the learner to make the toolbox explicit instead of hiding tool logic inside the run method.",
        "why_it_matters": "Tools become easier to understand, test, and extend when they are declared clearly.",
        "implementation_example": "self.tools = {\"fetch\": fetch_url}",
        "common_mistake": "Embedding tool behavior in run() without a visible registry or naming structure.",
        "example": "self.tools = {\"fetch\": fetch_url}",
    },
    {
        "id": 6,
        "slug": "tool-execution",
        "title": "Tool Execution",
        "description": "Actually use a tool in the flow.",
        "minutes": "12 min",
        "academy_order": 6,
        "check": "tool_execution",
        "capability": "Your agent reports that it used a tool.",
        "hint": "Call a tool and include it in tools_used.",
        "explanation": "This stage connects declared tools to an actual execution path so the learner sees a real action happen.",
        "why_it_matters": "A declared tool is only useful once the agent can actually use it during a run.",
        "implementation_example": "result = fetch_url(url)\nreturn {\"output\": result, \"tools_used\": [\"fetch_url\"], \"memory\": {}, \"error\": None}",
        "common_mistake": "Calling a tool but failing to report that usage back to the caller.",
        "example": "result = fetch_url(url)\nreturn {\"output\": result, \"tools_used\": [\"fetch_url\"], \"memory\": {}, \"error\": None}",
    },
    {
        "id": 7,
        "slug": "agent-loop",
        "title": "Agent Loop",
        "description": "Solve a simple multi-step prompt.",
        "minutes": "15 min",
        "academy_order": 7,
        "check": "agent_loop",
        "capability": "Your agent can handle a simple multi-step instruction.",
        "hint": "Teach the agent to combine steps instead of only matching one prompt pattern.",
        "explanation": "This stage moves beyond single-response behavior and teaches a lightweight reasoning loop that can follow a small sequence of instructions.",
        "why_it_matters": "The loop is what turns a one-off responder into something that can process small tasks with momentum.",
        "implementation_example": "if input_text == \"Add 1 to 3, then multiply by 2.\":\n    return {\"output\": \"8\", \"tools_used\": [], \"memory\": {}, \"error\": None}",
        "common_mistake": "Only handling one isolated prompt instead of showing a small reasoning flow.",
        "example": "if input_text == \"Add 1 to 3, then multiply by 2.\":\n    return {\"output\": \"8\", \"tools_used\": [], \"memory\": {}, \"error\": None}",
    },
    {
        "id": 8,
        "slug": "write-tool",
        "title": "Write Tool",
        "description": "Create your own tool helper.",
        "minutes": "20 min",
        "academy_order": 8,
        "check": "write_tool",
        "capability": "Your agent exposes at least one custom tool implementation.",
        "hint": "Add a tool your agent authors itself, then make it visible through the tool registry.",
        "explanation": "This stage focuses on tool authorship. The learner should move from using declared tools to writing one of their own.",
        "why_it_matters": "Writing a tool is a key transition from using the academy scaffold to shaping the agent's behavior.",
        "implementation_example": "def summarize(text: str) -> str:\n    return text.strip().lower()",
        "common_mistake": "Leaving the tool registry as a placeholder instead of adding a real custom helper.",
        "example": "def summarize(text: str) -> str:\n    return text.strip().lower()",
    },
    {
        "id": 9,
        "slug": "your-first-agent",
        "title": "Your First Agent",
        "description": "Finish the academy path with a complete agent.",
        "minutes": "25 min",
        "academy_order": 9,
        "check": None,
        "capability": "Your learning journey is complete.",
        "hint": "Review the full path and confirm the agent now feels like a complete project.",
        "explanation": "This final stage is the academy milestone. It marks the moment when the learner has progressed through the full guided path.",
        "why_it_matters": "A completion milestone gives the learner a clear finish line and a sense of achievement.",
        "implementation_example": "Review the entire agent and confirm every earlier milestone is complete.",
        "common_mistake": "Treating the finish line like another technical test instead of the academy completion moment.",
        "example": "Your agent is ready to run through the full learning path.",
    },
]


CAPABILITY_LABELS: dict[str, str] = {
    "project_structure": "Local Setup",
    "first_response": "First Output",
    "llm_connection": "Connect LLM",
    "tool_definition": "Tools",
    "tool_execution": "Tool Execution",
    "agent_loop": "Agent Loop",
    "write_tool": "Write Tool",
}


def capability_label(key: str) -> str:
    """Return a human-readable label for a capability key."""

    return CAPABILITY_LABELS.get(key, key.replace("_", " ").title())


def stage_description(stage: dict[str, Any]) -> str:
    """Return the academy description for display in the terminal."""

    return str(stage.get("description", stage["title"])).strip()


def stage_capability(stage: dict[str, Any]) -> str:
    """Return the learning outcome associated with a stage."""

    return str(stage.get("capability", stage_description(stage))).strip()


def stage_hint(stage: dict[str, Any]) -> str:
    """Return the learning hint attached to a stage."""

    return str(stage.get("hint", "")).strip()


def stage_example(stage: dict[str, Any]) -> str:
    """Return a concrete implementation example for a stage."""

    return str(stage.get("example", "")).strip()


def stage_explanation(stage: dict[str, Any]) -> str:
    """Return the explanatory text for a stage."""

    return str(stage.get("explanation", "")).strip()


def stage_why_it_matters(stage: dict[str, Any]) -> str:
    """Return the practical importance of a stage."""

    return str(stage.get("why_it_matters", "")).strip()


def stage_implementation_example(stage: dict[str, Any]) -> str:
    """Return the implementation example for a stage."""

    return str(stage.get("implementation_example", stage_example(stage))).strip()


def stage_common_mistake(stage: dict[str, Any]) -> str:
    """Return the common mistake associated with a stage."""

    return str(stage.get("common_mistake", "")).strip()


def stage_minutes(stage: dict[str, Any]) -> str:
    """Return the estimated minutes for a stage."""

    return str(stage.get("minutes", "")).strip()


def stage_slug(stage: dict[str, Any]) -> str:
    """Return the academy slug for a stage."""

    return str(stage.get("slug", "")).strip()


def resolve_stage(query: str) -> dict[str, Any] | None:
    """Resolve a user-supplied stage name, slug, capability, or id to a stage."""

    normalized = query.strip().lower()
    if not normalized:
        return None

    if normalized.isdigit():
        stage_id = int(normalized)
        for stage in STAGES:
            if stage["id"] == stage_id or stage.get("academy_order") == stage_id:
                return stage

    aliases = {
        "introduction": 1,
        "intro": 1,
        "local setup": 2,
        "local-setup": 2,
        "first output": 3,
        "first-response": 3,
        "connect llm": 4,
        "connect-llm": 4,
        "tools": 5,
        "tool execution": 6,
        "tool-execution": 6,
        "reasoning": 7,
        "agent loop": 7,
        "agent-loop": 7,
        "write tool": 8,
        "write-tool": 8,
        "your first agent": 9,
        "your-first-agent": 9,
        "project structure": 2,
    }
    if normalized in aliases:
        stage_id = aliases[normalized]
        for stage in STAGES:
            if stage["academy_order"] == stage_id or stage["id"] == stage_id:
                return stage

    for stage in STAGES:
        haystack = " ".join(
            str(stage.get(key, ""))
            for key in ("slug", "title", "description", "capability", "check", "hint", "explanation")
        ).lower()
        if normalized in haystack:
            return stage

    return None
