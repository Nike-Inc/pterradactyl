class BaseValidator(object):

  def __init__(self, root_module, facts):
    self.root_module = root_module
    self.facts = facts

  def validate(self):
    return True
