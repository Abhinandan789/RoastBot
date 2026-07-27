"""
registry.py - Selects which pet design module is active.

Add a new pet by dropping a module in this folder implementing
draw_idle/draw_happy/draw_angry/draw_sick(canvas, tick, tone_bucket),
then adding it to PET_REGISTRY below.
"""

from src.pets import smiley, droplet, cat, robot, ghost, smiley2

PET_REGISTRY = {
    "smiley": smiley,
    "droplet": droplet,
    "cat": cat,
    "robot": robot,
    "ghost": ghost,
    "smiley2": smiley2
}

DEFAULT_PET = "droplet"


def get_active_pet_module(pet_name=None):
    name = pet_name or DEFAULT_PET
    return PET_REGISTRY.get(name, PET_REGISTRY[DEFAULT_PET])