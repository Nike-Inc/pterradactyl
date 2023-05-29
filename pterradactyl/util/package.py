import importlib


def entry_points(group):
    return {c.name: c for c in importlib.metadata.entry_points(group=group)}
