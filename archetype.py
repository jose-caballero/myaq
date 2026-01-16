from sysadmin.bcolors import bcolors
from sysadmin.myshell import run

class Archetype(object):
    def __init__(self, name='ral-tier1'):
        self.name = name
        self.info = None

    def __str__(self):
        """
        Human friendly representation of this Archetype
        """
        out = ""
        out += '\n' + bcolors.WARNING + 'archetype:   ' + bcolors.ENDC + self.name
        if len(self.features):
            out += '\n' + bcolors.WARNING + 'features:    ' + bcolors.ENDC + self.features[0].name
            for feature in self.features[1:]:
                out += '\n' + '             ' + feature.name
        else:
            out += '\n' + bcolors.WARNING + 'features:       ' + bcolors.ENDC
        return out

    @property
    def features(self):
        """
        get the Features bound to this Archetype 
        """
        from myaq.feature import Feature, FeatureList
        if not self.info:
            self._show_archetype()
        feature_l = FeatureList()
        for line in self.info.split('\n'):
            if 'Host Feature' in line:
                featurename = line.split()[2]
                feature = Feature(featurename)
                feature_l.append(feature)
        return feature_l

    def _show_archetype(self):
        cmd = "/opt/aquilon/bin/aq.py show_archetype --archetype %s" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info


class ArchetypeList(list):

    def __str__(self):
        out = ""
        for a in self.__iter__():
            out += str(a)
            out += '\n'
        return out


