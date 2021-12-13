import pkg_resources


def entry_points(group):
    return {c.name: c for c in pkg_resources.iter_entry_points(group=group)}
