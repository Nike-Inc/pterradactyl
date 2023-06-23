from importlib import metadata


def entry_points(group):
    return {c.name: c for c in metadata.entry_points(group=group)}
