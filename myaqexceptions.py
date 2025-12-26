# ------------------------------------------------------------------------------ 
#   Sandbox
# ------------------------------------------------------------------------------ 

class NoSandboxException(Exception):
    def __init__(self):
        self.value = 'No sandbox name provided and current location is not a sandbox'
    def __str__(self):
        return repr(self.value)

class SandboxRebaseFailure(Exception):
    def __init__(self, sandbox, results):
        self.value = 'Rebasing sandbox %s has failed.' %sandbox
        self.results = results
    def __str__(self):
        return repr(self.value)

class SandboxNameTooLong(Exception):
    def __init__(self, sandbox):
        self.value = 'Sandbox name %s is too long.' %sandbox
    def __str__(self):
        return repr(self.value)
    
class SandboxExists(Exception):
    def __init__(self, sandbox):
        self.value = 'Sandbox %s already exists.' %sandbox
    def __str__(self):
        return repr(self.value)

# ------------------------------------------------------------------------------ 
#   Personality
# ------------------------------------------------------------------------------ 

class PersonalityExists(Exception):
    def __init__(self, personality):
        self.value = 'Personality %s already exists.' %personality
    def __str__(self):
        return repr(self.value)

# ------------------------------------------------------------------------------ 
#   Feature
# ------------------------------------------------------------------------------ 

class FeatureExists(Exception):
    def __init__(self, feature):
        self.value = 'Feature %s already exists.' %feature
    def __str__(self):
        return repr(self.value)
