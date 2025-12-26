from myaq.archetype import Archetype
from myaq.personality import Personality
from myaq.operatingsystem import OperatingSystem


class Profile(object):
    """
    class just to aggregate profile components for Hosts
    and return the *values* of the components
    """
    def __init__(self, personality=None, archetype=None, os=OperatingSystem()):
        """ 
        :param Personality personality:
        :param Archetpy archetype: 
        :param OperatingSystem os:
        """ 
        self.personality = personality 
        self.archetype = archetype
        self.os = os

    @property
    def osname(self):
        try:
            return self.os.name
        except Exception as ex:
            return None

    @property
    def osversion(self):
        try:
            return self.os.version
        except Exception as ex:
            return None

