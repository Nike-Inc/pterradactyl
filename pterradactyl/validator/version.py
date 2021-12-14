import logging
import pterradactyl

from semantic_version import SimpleSpec, Version

from pterradactyl.config import Config
from pterradactyl.validator.base import BaseValidator

log = logging.getLogger(__name__)

class VersionValidator(BaseValidator):

  def validate(self):
    config = Config()
    requirement = config.get('pterradactyl', {}).get('version', None)
    if requirement is not None:
      spec = SimpleSpec(requirement)
      version = Version(pterradactyl.__version__)
      
      if not spec.match(version):
        log.error("{package} version {version} doesn't meet requirement '{spec}' defined in {config_file}.".format(
          package=pterradactyl.__package__, version=version, spec=spec, config_file=config.file))
        return False
