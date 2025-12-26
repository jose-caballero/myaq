import re

from bcolors import bcolors
from sysadmin.myshell import run
from myaq.personality import Personality, PersonalityList
from myaq.archetype import Archetype, ArchetypeList

# ============================================================================== 
# NOTE: this class is under development / to be tested
# ============================================================================== 
class FeatureHandler(object):
    """
    class to create and remove Features
    """
    def create(self, name):
        cmd = '/opt/aquilon/bin/aq.py add_feature --feature %s --type host' %name
        results = run(cmd)
        if results.rc == 0:
            feature = Feature(name)
            return feture
        else:
            return None

    def remove(self, feature):
        """
        removes a Feature
        """
        cmd = '/opt/aquilon/bin/aq.py del_feature --feature %s --type host' %self.feature.name
        results = run(cmd)
        return results
        
    @property
    def full_list(self):
        """
        returns a FeatureList with all Features in Aquilon
        """
        feature_l = FeatureList()
        cmd = 'aq show_feature --all'
        results = run(cmd)
        for line in results.out.split('\n'):
            line = line.strip()
            if line.startswith('Host Feature:'):
                feature_name = line.split()[-1]
                feature = Feature(feature_name)
                feature_l.append(feature)
        return feature_l


class Feature(object):
    def __init__(self, name):
        self.name = name 
        self.info = None

    def __str__(self):
        """
        Human friendly representation of this Feature
        """
        template = self.template
        personalities = self.personalities
        archetypes = self.archetypes

        out = bcolors.WARNING + 'name:                ' + bcolors.ENDC + self.name
        ###out += '\n' + bcolors.WARNING + 'template:            ' + bcolors.ENDC + template
        if personalities:
            out += '\n' + bcolors.WARNING + 'personalities:       ' + bcolors.ENDC + personalities[0].archetype.name + ' / ' + personalities[0].name 
            for personality in personalities[1:]:
                out += '\n' + '                     ' + personality.archetype.name + ' / ' + personality.name
        else:
            out += '\n' + bcolors.WARNING + 'personalities:       ' + bcolors.ENDC
        if archetypes:
            out += '\n' + bcolors.WARNING + 'archetypes:          ' + bcolors.ENDC + archetypes[0].name 
            for archetype in archetypes[1:]:
                out += '\n' + '                        ' + archetype.name
        else:
            out += '\n' + bcolors.WARNING + 'archetypes:          ' + bcolors.ENDC
        out += '\n'
        return out

    def _show_feature(self):
        cmd = "/opt/aquilon/bin/aq.py show_feature --feature %s --type host" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info

    @property
    def exists(self):
        """
        checks if the Feature actually exists in Aquilon or not
        """
        cmd = "/opt/aquilon/bin/aq.py show_feature --feature %s --type host" %self.name
        r = run(cmd)
        return r.rc == 0

    @property
    def template(self):
        if not self.info:
            self._show_feature()
        for line in self.info.split('\n'):
            if 'Template' in line:
                # FIXME !! use class Template
                template = line.split(':')[1].strip()
                return template

    @property
    def personalities(self):
        """
        gets the Personalities binding this Feature
        """
        if not self.info:
            self._show_feature()
        personalities = PersonalityList()
        for line in self.info.split('\n'):
            line = line.strip()
            if line.startswith('Bound to: Personality'):
                personality_name = line.split()[-1]
                p = Personality(personality_name)
                personalities.append(p)
        return personalities

    @property
    def archetypes(self):
        """
        gets the Archetypes binding this Feature
        """
        if not self.info:
            self._show_feature()
        archetypes = ArchetypeList()
        for line in self.info.split('\n'):
            line = line.strip()
            if line.startswith('Bound to: Archetype'):
                archetype_name = line.split()[-1]
                p = Archetype(archetype_name)
                archetypes.append(p)
        return archetypes

    @property
    def hosts(self):
        """
        gets the list of Hosts using this Feature
        """
        from myaq.host import Host, HostList
        cmd = 'aq search_host --feature %s' %self.name
        results = run(cmd)
        host_l = HostList()
        for hostname in results.out.split():
            host = Host(hostname)
            host_l.append(host)
        return host_l

    def create(self, eon_id=15):
        """
        create this Feature
        """
        cmd = '/opt/aquilon/bin/aq.py add_feature --feature %s --type host  --eon_id %s' %(self.name, eon_id)
        results = run(cmd)
        return results

    def remove(self):
        """
        remove this Feature
        """
        cmd = '/opt/aquilon/bin/aq.py del_feature --feature %s --type host' %self.name
        results = run(cmd)
        return results


class FeatureList(list):

    def __str__(self):
        out = ""
        for f in self.__iter__():
            out += str(f)
            out += '\n'
        return out

    @property
    def name_list(self):
        """
        returns a list with the Feature names
        """
        name_l = []
        for feature in self.__iter__():
            name = feature.name
            name_l.append(name)
        name_l.sort()
        return name_l 

    def set(self, name_l):
        if name_l:
            # just in case a client calls this method with value None
            for name in name_l:
                self.append(Feature(name))

    def find(self, pattern=None):
        """
        find all Features registered in Aquilon
        """
        cmd = 'aq show_feature --all'
        results = run(cmd)
        for line in results.out.split('\n'):
            if line.startswith('Host Feature:'):
                name = line.split()[2]
                if not pattern or re.search(pattern, name):
                    self.append(Feature(name))

    def create(self, eon_id=15):
        for feature in self.__iter__():
            feature.create(eon_id)

    def remove(self):
        for feature in self.__iter__():
            feature.remove()

    def filter(self, pattern_l):
        """
        returns a new List containing only the 
        Features matchiing any of the patterns
        """
        new_feature_l = FeatureList()
        for feature in self.__iter__():
            for pattern in pattern_l:
                if pattern in feature.name:
                    new_feature_l.append(feature)
                    continue
        return new_feature_l

