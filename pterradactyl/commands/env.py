from .manifest import ManifestCommand


class EnvCommand(ManifestCommand):
    subcommands = ["new", "list", "select", "delete"]
