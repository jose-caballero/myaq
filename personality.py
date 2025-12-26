import re

from bcolors import bcolors
from sysadmin.myshell import run

from myaq.archetype import Archetype


# ============================================================================== 
# NOTE: this class is under development / to be tested
# ============================================================================== 
class PersonalityHandler(object):
    """
    class to create and destroy Personality objects
    """
    def __init__(self):
        pass

    def create(self, name, eon_id=15):
        """
        default eon_id = 15 (DCIG)
        """
        if '/' in name:
            archetypename, name = name.split('/')
            name = name
            archetype = Archetype(archetypename)
        else:
            name = name
            archetype = Archetype('ral-tier1')

        cmd = "/opt/aquilon/bin/aq.py add_personality --personality %s --archetype %s --eon_id %s" %(name, archetype.name, eon_id)
        results = run(cmd)
        if results.rc == 0:
            personality = Personality(name)
            return personality
        else:
            return None

    def remove(self, personality):
        """
        remove the Personality
        """
        name = personality.name
        archetype = personality.archetype
        cmd = "/opt/aquilon/bin/aq.py del_personality --personality %s --archetype %s" %(name, archetype.name)
        results = run(cmd)
        self.info = results.out
        return self.info

    def clone(self, personality, name):
        """
        clone existing Personality "personality" into a new one with name "name"
        """
        new_personality = self.create(name)
        new_personality.copy_features(personality)
        return new_personality

    @property
    def full_list(self):
        """
        returns a PersonalityList with all Personalities in Aquilon
        """
        personality_l = PersonalityList()
        cmd = 'aq show_personality --all'
        results = run(cmd)
        for line in results.out.split('\n'):
            line = line.strip()
            if line.startswith('Host Personality'):
                personality_name = line.split()[2]
                personality = Personality(personality_name)
                personality_l.append(personality)
        return personality_l
        

class Personality(object):
    def __init__(self, name, archetype=Archetype('ral-tier1')):
        self._archetype = archetype
        if '/' in name:
            arch = name.split('/')[0]
            self._archetype = Archetype(arch)
            self.name = name.split('/')[1]
        else:
            self.name = name
        self.info = None

    def __str__(self):
        """
        Human friendly representation of this Personality
        """
        out = ""
        out += '\n' + bcolors.WARNING + 'personality: ' + bcolors.ENDC + self.name
        out += '\n' + bcolors.WARNING + 'archetype:   ' + bcolors.ENDC + self.archetype.name
        out += '\n' + bcolors.WARNING + 'owner:       ' + bcolors.ENDC + self.owner
        if len(self.features):
            out += '\n' + bcolors.WARNING + 'features:    ' + bcolors.ENDC + self.features[0].name
            for feature in self.features[1:]:
                out += '\n' + '             ' + feature.name
        else:
            out += '\n' + bcolors.WARNING + 'features:       ' + bcolors.ENDC
        if len(self.hosts):
            out += '\n' + bcolors.WARNING + 'hosts:       ' + bcolors.ENDC + self.hosts[0].name
            for host in self.hosts[1:]:
                out += '\n' + '             ' + host.name
        else:
            out += '\n' + bcolors.WARNING + 'hosts:       ' + bcolors.ENDC
        return out

    def _show_personality(self):
        cmd = "/opt/aquilon/bin/aq.py show_personality --personality %s" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info

    @property
    def exists(self):
        """
        checks if the Feature actually exists in Aquilon or not
        """
        cmd = "/opt/aquilon/bin/aq.py show_personality --personality %s" %self.name
        r = run(cmd)
        return r.out != ""

    @property
    def features(self):
        """
        get the Features bound to this Personality
        """
        from myaq.feature import Feature, FeatureList
        if not self.info:
            self._show_personality()
        feature_l = FeatureList()
        for line in self.info.split('\n'):
            if 'Host Feature' in line:
                featurename = line.split()[2]
                feature = Feature(featurename)
                feature_l.append(feature)
        return feature_l 

    @property
    def hosts(self):
        """
        get the list of hosts bound to this personality
        """
        from myaq.host import Host, HostList
        cmd = 'aq search_host --personality %s' %self.name
        results = run(cmd)
        # FIXME
        # check rt == 0, otherwise raise an Exception
        hostlist = HostList()
        for name in results.out.split():
            host = Host(name)
            hostlist.append(host)
        return hostlist

    @property 
    def archetype(self):
        """
        get the archetype str for this Personality
        """
        if not self._archetype:
            if not self.info:
                self._show_personality()
            for line in self.info.split('\n'):
                if 'Archetype' in line:
                    archetype_name = line.split()[-1].strip()
                    self._archetype = Archetype(archetype_name)
                    break
        return self._archetype

    @property 
    def owner(self):
        """
        get the owner str for this Personality
        """
        if not self.info:
            self._show_personality()
        for line in self.info.split('\n'):
            if 'Owned by GRN' in line:
                owner = line.split(':')[1].strip()
                break
        return owner 

    def create(self, eon_id=15):
        """
        create the Personality.
        Assume archetype is 'ral-tier1'
        default owner / eon_id = 15 (DCIG)
        """
        cmd = "/opt/aquilon/bin/aq.py add_personality --personality %s --archetype %s --eon_id %s" %(self.name, self.archetype.name, eon_id)
        results = run(cmd)
        self.info = results.out
        return self.info

    def remove(self):
        """
        remove the Personality
        """
        cmd = "/opt/aquilon/bin/aq.py del_personality --personality %s --archetype %s" %(self.name, self.archetype.name)
        results = run(cmd)
        self.info = results.out
        return self.info

    def copy_features(self, source):
        """
        makes this Personality to be a copy from another one.
        Assume archetype is 'ral-tier1'
        :param Personality source: personality to copy from
        """
        #self.info = None # just in case
        #cmd = "/opt/aquilon/bin/aq.py add_personality --personality %s --archetype %s --eon_id %s --copy_from %s" %(self.name, self.archetype.name, self.eon_id, source.name)
        #results = run(cmd)
        #self.info = results.out
        #return results
        feature_list = source.features
        self.bind(feature_list)

    def bind(self, feature_l):
        """
        bind a list of Features to this Personality
        """
        results = []
        for feature in feature_l:
            r = self.bind_feature(feature)
            results.append(r)
        return results

    def bind_feature(self, feature):
        """
        bind a single Feature to this Personality
        """
        cmd = 'aq bind_feature --personality %s --feature %s --justification tcm=00000' %(self.name, feature.name)
        results = run(cmd)
        self.info = results.out
        return results

    def unbind(self, feature_l):
        """
        unbind a list of Features to this Personality
        """
        results = []
        for feature in feature_l:
            r = self.unbind_feature(feature)
            results.append(r)
        return results

    def unbind_feature(self, feature):
        """
        unbind a single Feature to this Personality
        """
        cmd = 'aq unbind_feature --personality %s --feature %s --justification tcm=00000' %(self.name, feature.name)
        results = run(cmd)
        self.info = results.out
        return results


class PersonalityList(list):

    def __str__(self):
        out = ""
        for p in self.__iter__():
            out += str(p)
            out += '\n'
        return out

    @property
    def hosts(self):
        from myaq.host import HostList 
        host_l = HostList()
        for personality in self.__iter__():
            host_l += personality.hosts
        return host_l

    def set(self, name_l):
        for name in name_l:
            self.append(Personality(name))

    def find(self, pattern=None):
        """
        find all Personalities registered in Aquilon
        """
        cmd = 'aq show_personality --all'
        results = run(cmd)
        for line in results.out.split('\n'):
            if line.startswith('Host Personality:'):
                name = line.split()[2]
                if not pattern or re.search(pattern, name):
                    archetype_name = line.split()[-1]
                    p = Personality(name, Archetype(archetype_name))
                    self.append(p)

    def create(self, owner=15):
        for personality in self.__iter__():
            personality.create(owner)

    def bind(self, feature_l):
        for personality in self.__iter__():
            personality.bind(feature_l)

    def bind_feature(self, feature):
        for personality in self.__iter__():
            personality.bind_feature(feature)

    def unbind(self, feature_l):
        for personality in self.__iter__():
            personality.unbind(feature_l)

    def unbind_feature(self, feature):
        for personality in self.__iter__():
            personality.unbind_feature(feature)

    def filter(self, pattern_l):
        """
        returns a new List containing only the
        Personalities matchiing any of the patterns
        """
        new_personality_l = PersonalityList()
        for personality in self.__iter__():
            for pattern in pattern_l:
                if pattern in personality.name:
                    new_personality_l.append(personality)
                    continue
        return new_personality_l
