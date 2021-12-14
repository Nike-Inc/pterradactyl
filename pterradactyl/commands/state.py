from .manifest import ManifestCommand


class StateCommand(ManifestCommand):
    subcommands = ["list", "mv", "pull", "push", "rm", "show"]
