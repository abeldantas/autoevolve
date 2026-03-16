#!/usr/bin/env python3
"""
D20 mutation roll for autoevolve.

Generates a random number 1-20 and maps it to a mutation strategy.
The evolution controller runs this before proposing a mutation to
determine what KIND of mutation to attempt this cycle.

Usage:
    python3 roll.py
    python3 roll.py --json
"""

import json
import random
import sys

MUTATION_TABLE = {
    # 1: Critical fail — skip this cycle
    1: {
        "category": "skip",
        "name": "Natural 1 — Rest cycle",
        "description": "Skip this cycle entirely. No mutation proposed. Sometimes the best change is no change.",
    },
    # 2-5: Simplification (remove/consolidate)
    2: {
        "category": "simplify",
        "name": "Remove dead weight",
        "description": "Find and remove an instruction the agent likely ignores. Look for rules with zero signals across multiple windows.",
    },
    3: {
        "category": "simplify",
        "name": "Consolidate scattered rules",
        "description": "Find related instructions spread across different sections and merge them into one clear block.",
    },
    4: {
        "category": "simplify",
        "name": "Kill redundancy",
        "description": "Find two rules that say the same thing. Delete one. Pick the clearer one to keep.",
    },
    5: {
        "category": "simplify",
        "name": "Shorten a verbose rule",
        "description": "Find the longest instruction and rewrite it in half the lines without losing meaning.",
    },
    # 6-10: Specificity (make existing rules concrete)
    6: {
        "category": "specify",
        "name": "Vague to specific",
        "description": "Find a vague adjective-based rule ('be concise', 'be thorough') and replace it with concrete criteria.",
    },
    7: {
        "category": "specify",
        "name": "Add an example",
        "description": "Pick an existing rule and add a concrete example of correct behavior. Agents follow examples better than abstract rules.",
    },
    8: {
        "category": "specify",
        "name": "Add a counter-example",
        "description": "Pick an existing rule and add a 'DO NOT' case — show what the wrong behavior looks like.",
    },
    9: {
        "category": "specify",
        "name": "Sharpen a conditional",
        "description": "Find an 'if/when' rule that's ambiguous about its trigger. Make the trigger condition explicit.",
    },
    10: {
        "category": "specify",
        "name": "Quantify a threshold",
        "description": "Find a rule that says 'too many', 'too long', 'a lot' and replace it with a number.",
    },
    # 11-14: Signal-driven (respond to observed patterns)
    11: {
        "category": "signal-driven",
        "name": "Fix a correction pattern",
        "description": "Look at correction signals. Find the most common correction topic and add a rule to prevent it.",
    },
    12: {
        "category": "signal-driven",
        "name": "Reinforce a positive",
        "description": "Look at positive signals. Identify what behavior earned praise and make sure it's explicitly documented as a rule.",
    },
    13: {
        "category": "signal-driven",
        "name": "Clarify a confusion zone",
        "description": "Look for task_complete with corrections > 0. The instruction for that area is unclear — rewrite it.",
    },
    14: {
        "category": "signal-driven",
        "name": "Resolve a contradiction",
        "description": "Look for contradictory signals (positive and negative for same behavior). The rule is ambiguous — clarify when to apply vs when not to.",
    },
    # 15-17: Procedural (change how the agent works)
    15: {
        "category": "procedural",
        "name": "Optimize a workflow",
        "description": "Find a multi-step procedure and look for a step that could be eliminated or reordered for efficiency.",
    },
    16: {
        "category": "procedural",
        "name": "Add a checklist",
        "description": "Find a complex task the agent does repeatedly and add a short checklist to ensure consistency.",
    },
    17: {
        "category": "procedural",
        "name": "Change a default",
        "description": "Find a behavior where the agent asks for confirmation but could safely default to one option. Or vice versa.",
    },
    # 18-19: Bold moves (bigger changes, higher risk/reward)
    18: {
        "category": "bold",
        "name": "Rewrite a section",
        "description": "Pick one section of the agent's instructions and rewrite it from scratch. Keep the intent, improve the clarity. Stay within mutation size limits.",
    },
    19: {
        "category": "bold",
        "name": "Personality nudge",
        "description": "Make a small, targeted adjustment to tone or communication style based on signal patterns. Keep it subtle.",
    },
    # 20: Natural 20 — freak mutation
    20: {
        "category": "freak",
        "name": "Natural 20 — Freak mutation",
        "description": "Go wild. Propose something unexpected — a new section, a radical simplification, a creative rule no one would think of. The human will review it anyway, so take the risk. This is how breakthroughs happen.",
    },
}


def roll():
    return random.randint(1, 20)


def main():
    result = roll()
    mutation = MUTATION_TABLE[result]

    if "--json" in sys.argv:
        print(json.dumps({"roll": result, **mutation}, indent=2))
    else:
        print(f"d20 roll: {result}")
        print(f"Category: {mutation['category']}")
        print(f"Strategy: {mutation['name']}")
        print(f"")
        print(mutation["description"])


if __name__ == "__main__":
    main()
