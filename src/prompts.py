"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS - Symbol Reordering
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Rearrange the symbols from their initial positions to match the exact target configuration. Each symbol must move to its designated final position.",
        "Reorder the symbols to transform the initial sequence into the target sequence. All symbols must be repositioned to achieve the exact final arrangement.",
        "Animate the symbols moving from the initial arrangement to the target arrangement. Each symbol transitions smoothly to its specified final position.",
    ],

    "with_labels": [
        "Rearrange the symbols from positions in the first image to match the positions shown in the final image. Each symbol moves to its exact target location.",
        "Transform the initial symbol sequence into the target sequence by moving each symbol to its designated final position as shown in the goal state.",
        "Reorder the symbols: move each symbol from its starting position to its ending position to achieve the exact configuration shown in the final image.",
    ],

    "simple": [
        "Move the symbols to match the target arrangement.",
        "Rearrange the symbols to achieve the goal configuration.",
        "Reorder the symbols from the initial state to the final state.",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
