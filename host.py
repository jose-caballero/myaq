import os
import re
import time

from sysadmin.bcolors import bcolors
from sysadmin.myshell import run

from myaq.archetype import Archetype
from myaq.personality import Personality
from myaq.location import Domain, DomainList, Sandbox, SandboxList
from myaq.cluster import Cluster
from myaq.interface import Interface
from myaq.service  import Service
from myaq.machine import Machine
from myaq.model import Model
from myaq.rack import Rack
from myaq.vendor import Vendor


def Host(hostname):
    """
    returns an object of the right HostXYZ( )
    """
    wn_pattern = '^lcg[0-9]{4}\.gridpp\.rl\.ac\.uk$'
    vm_pattern = '^host-\d{1,3}-\d{1,3}-\d{1,3}-\d{1,3}\.nubes\.stfc\.ac\.uk$'

    if re.match(wn_pattern, hostname):
        return HostWN(hostname)
    elif re.match(vm_pattern, hostname):
        return HostOpenStack(hostname)
    else:
        return HostProduction(hostname)


class HostBase(object):
    def __init__(self, name):
        self.name = name
        self.info = None

    def __str__(self):
        """
        Human friendly representation of this Host
        """
        out = bcolors.WARNING + 'hostname:            ' + bcolors.ENDC + self.name
        out += '\n' + bcolors.WARNING + 'archetype:           ' + bcolors.ENDC + self.archetype.name
        out += '\n' + bcolors.WARNING + 'operating system:    ' + bcolors.ENDC + self.os + ' / ' + self.version
        if self.location.category == "Domain":
            out += '\n' + bcolors.WARNING + 'domain:              ' + bcolors.ENDC + self.location.name
        if self.location.category == "Sandbox":
            out += '\n' + bcolors.WARNING + 'sandbox:             ' + bcolors.ENDC + self.location.name
        out += '\n' + bcolors.WARNING + 'owner:               ' + bcolors.ENDC + self.owner
        out += '\n' + bcolors.WARNING + 'personality:         ' + bcolors.ENDC + self.personality.name
        features = self.personality.features
        if features:
            out += '\n' + bcolors.WARNING + 'features:            ' + bcolors.ENDC + features[0].name
            for feature in features[1:]:
                out += '\n' + '                     ' + feature.name
        if self.cluster:
            out += '\n' + bcolors.WARNING + 'cluster:             ' + bcolors.ENDC + self.cluster.name
            if self.cluster.service:
                out += '\n' + bcolors.WARNING + '  service/instance:  ' + bcolors.ENDC + self.cluster.service.name + ' / ' + self.cluster.service.instance
        if self.service:
            out += '\n' + bcolors.WARNING + 'service/instance:    ' + bcolors.ENDC + self.service.name + ' / ' + self.service.instance
        out += '\n'
        return out

    def _show_host(self):
        cmd = "/opt/aquilon/bin/aq.py show_host --hostname %s" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info

    def update(self):
        self._show_host()

    @property
    def short_name(self):
        short = self.name.split('.')[0]
        return short

    @property
    def owner(self):
        """
        get the Owner for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Owned by GRN' in line:
                owner = line.split(':')[1].strip()
                return owner 

    @property
    def personality(self):
        """
        get the Personality for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Host Personality' in line:
                name = line.split()[2].strip()
                personality = Personality(name)
                return personality

    @property
    def archetype(self):
        """
        get the Archetype for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Host Archetype' in line:
                archetype_name = line.split()[2].strip()
                return Archetype(archetype_name)

    @property
    def rack(self):
        """
        get the Rack for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Rack' in line:
                rack = line.split(':')[1].strip()
                return Rack(rack)

    @property
    def interfaces(self):
        """
        get the list of Interfaces
        """
        if not self.info:
            self._show_host()
        out = []

        in_i_block = False
        for line in self.info.split('\n'):
            if re.search(r"^\s{2}(?!\s).*$", line):
                if in_i_block:
                    out.append(Interface(name, addr, ip, network_interface))
                    in_i_block = False
                if line.startswith('  Interface'):
                    in_i_block = True
                    name = line.split()[1].strip()
                    addr = line.split()[2].strip()
                    ip = ""
                    network_interface = None
            if 'Provides' in line:
                match = re.search(r"\[(.*?)\]", line)
                if match:
                    ip = match.group(1)
            if 'Network Environment' in line:
                network_interface = line.split()[-1]

        return out


    @property
    def vendor(self):
        """
        get the Vendor for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if line.startswith('  Vendor:'):
                vendor = line.split()[1].strip()
                return Vendor(vendor)

    @property
    def model(self):
        """
        get the Model for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            # Note that the output of "aq show_host" includes more than one line with string "Model".
            # We need to select the one that starts with "  Vendor" (with two white spaces). Example:
            #   Vendor: dell Model: wn-2019-dell
            if line.startswith('  Vendor'):
                model = line.split()[-1].strip()
                return Model(model)

    @property
    def location(self):
        """
        get either the Sandbox or the Domain for the host
        """
        if not self.info:
            self._show_host()

        for line in self.info.split('\n'):
            if 'Domain' in line:
                name = line.split()[1].strip()
                domain = Domain(name)
                return domain
            if 'Sandbox' in line:
                name = line.split()[1].strip()
                sandbox = Sandbox(name)
                return sandbox


    @property
    def domain(self):
        """
        get the Domain for a given hostname
        """
        if self.location.category == 'Domain':
            return self.location
        else:
            return None

    @property
    def sandbox(self):
        """
        get the Sandbox for a given hostname
        """
        if self.location.category == 'Sandbox':
            return self.location
        else:
            return None

    @property
    def version(self):
        """
        get the Operating System version for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Version' in line:
                version  = line.split()[1].strip()
                return version

    @property
    def os(self):
        """
        get the Operating System name for a given hostname
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Operating System' in line:
                os = line.split()[2].strip()
                return os

    @property
    def cluster(self):
        """
        get the Cluster for this Host
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Member of ral-tier1-clusters' in line:
                cluster = line.split()[-1].strip()
                return Cluster(cluster)
        else:
            # The Host is not part of any Cluster
            return None

    @property
    def service(self):
        """
        get the Service for this Host
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if 'Provides Service' in line:
                service = line.split()[2].strip()
                instance = line.split()[-1].strip()
                return Service(service, instance)
        else:
            # The Host is not part of any Service
            return None

    @property
    def machine(self):
        """
        get the Machine for this Host
        """
        if not self.info:
            self._show_host()
        for line in self.info.split('\n'):
            if line.startswith('Machine:'):
                name = line.split()[1].strip()
                machine = Machine(name)
                return machine

    def make(self, archetype=None, personality=None):
        """
        compile the host
        """
        cmd = 'aq make --hostname %s' %self.name
        if archetype:
            cmd += ' --archetype %s' %archetype.name
        if personality:
            cmd += ' --personality %s' %personality.name
        results = run(cmd)
        return results

    def make_profile(self, profile):
        """
        compile the host
        """
        cmd = 'aq make --hostname %s' %self.name
        if profile.personality:
            cmd += ' --personality %s' %profile.personality.name
        if profile.archetype:
            cmd += ' --archetype %s' %profile.archetype.name
        cmd += ' --osname %s' %profile.osname
        cmd += ' --osversion %s' %profile.osversion
        results = run(cmd)
        return results

    def pxeswitch_install(self):
        """
        installs the host with pxeswitch
        """
        cmd = 'aq pxeswitch --install --hostname %s' %self.name
        results = run(cmd)
        return results

    def manage_to_domain(self):
        """
        manage this Host to domain prod (default)
        """
        from myaq.location import Domain
        domain = Domain('prod')
        domain._manage_host(self)


    def restore(self):
        """
        manaage this Host back to a given Domain and recompile it
        """
        self.manage_to_domain()
        self.make()

    def uncluster(self):
        """
        if this Host is part of a Cluster, remove it from it
        """
        cluster = self.cluster
        if cluster:
            cluster.remove_host(self)

    def remove(self):
        """
        remove this Host.
        Nothing by default, only for VMs, by overriding this method.
        """
        pass


    def remove_interface(self, interface):
        """
        remove a given interface
        """
        cmd = 'aq del_interface --machine %s --interface %s' %(self.machine, interface.name)
        results = run(cmd)
        return results

class HostWN(HostBase):
    def __init__(self, hostname):
        super(HostWN, self).__init__(hostname)
        self.host_type = 'hostwn'

    def __str__(self):
        out = super(HostWN, self).__str__()
        out = out[:-1] # to remove the existing white line at the end
        out += '\n' + bcolors.WARNING + 'model:               ' + bcolors.ENDC + self.model.name
        out += '\n' + bcolors.WARNING + 'rack:                ' + bcolors.ENDC + self.rack.name
        out += '\n'
        return out

    @property
    def numerical_name(self):
        """
        assuming hostname is like 'lcg1234.gridpp.rl.ac.uk', returns '1234'
        """
        return self.name[3:7]

    def manage_to_domain(self):
        """
        manage this Host WN to domain prod_batch
        """
        from myaq.location import Domain
        domain = Domain('prod_batch')
        domain._manage_host(self)


class HostOpenStack(HostBase):
    def __init__(self, hostname):
        super(HostOpenStack, self).__init__(hostname)
        self.host_type = 'hostopenstack'

    def remove(self):
        """
        remove this Host
        """
        results = []
        # if host is part of a cluster, remove it from it first
        cluster = self.cluster
        if cluster:
            cluster.remove_host(self)
        # if host is a provider for a service, unbind it first
        service = self.service
        if service:
            service.unbind_host(self)
        # remove the host
        cmd = 'aq del_host --hostname %s' %self.name
        results = run(cmd)
        # remove the machine
        machine = self.machine
        machine.remove()
        # FIXME
        return results

    def make(self, archetype=None, personality=None):
        """
        compile the host
        """
        cmd = 'aq make --hostname %s' %self.name
        if archetype:
            cmd += ' --archetype %s' %archetype.name
        if personality:
            cmd += ' --personality %s' %personality.name
        # special flags for VMs
        cmd += ' --osname sl --osversion 7x-x86_64'
        results = run(cmd)
        return results

    def make_profile(self, profile):
        """
        compile the host
        """
        cmd = 'aq make --hostname %s' %self.name
        if profile.personality:
            cmd += ' --personality %s' %profile.personality.name
        cmd += ' --archetype %s' %profile.archetype.name
        cmd += ' --osname %s' %profile.osname
        cmd += ' --asversion %s' %profile.osversion
        results = run(cmd)
        return results


class HostProduction(HostBase):
    def __init__(self, hostname):
        super(HostProduction, self).__init__(hostname)
        self.host_type = 'hostproduction'



class HostList(list):

    def __str__(self):
        out = ""
        for host in self.__iter__():
            out += str(host)
            out += '\n'
        out = out.strip() # to remove the last '\n' character
        return out

    @property
    def names(self):
        l = []
        for host in self.__iter__():
            name = host.name
            l.append(name)
        return l

    def print_names(self):
        for host in self.__iter__():
            name = host.name
            print(name)

    def set(self, hostname_l):
        if hostname_l:
            # just in case a client calls this method with value None
            for hostname in hostname_l:
                self.append(Host(hostname))

    def make(self, archetype=None, personality=None):
        results_l = []
        for host in self.__iter__():
            r = host.make(archetype, personality)
            results_l.append(r)
        return results_l

    def make_profile(self, profile):
        results_l = []
        for host in self.__iter__():
            r = host.make(profile)
            results_l.append(r)
        return results_l

    def pxeswitch_install(self):
        for host in self.__iter__():
            host.pxeswitch_install()

    def manage_to_domain(self):
        """
        manage a list of Hosts to a given Domain:
            - "prod", by default
            - "prod_batch", for WNs
        """
        for host in self.__iter__():
            host.manage_to_domain()

    def restore(self):
        """
        manaage a list of Hosts back to a given Domain and recompile them
        """
        for host in self.__iter__():
            host.restore()

    def uncluster(self):
        """
        if needed, remote Hosts from their Cluster
        """
        for host in self.__iter__():
            host.uncluster()

    def remove(self):
        """
        remove a list of Hosts
        """
        for host in self.__iter__():
            host.remove()

    @property
    def sandbox_l(self):
        """
        return a SandboxList object for all distinct sandboxes
        """
        sandbox_name_l = []
        for host in self.__iter__():
            sandbox = host.sandbox
            # if sandbox is not None
            if sandbox:
                if sandbox.name not in sandbox_name_l:
                    sandbox_name_l.append(sandbox.name)
        sandboxlist = SandboxList()
        sandboxlist.set(sandbox_name_l)
        return sandboxlist

    @property
    def domain_l(self):
        """
        return a DomainList object for all distinct domains 
        """
        domain_name_l = []
        for host in self.__iter__():
            domain = host.domain
            # if domain is not None
            if domain:
                if domain.name not in domain_name_l:
                    domain_name_l.append(domain.name)
        domainlist = DomainList()
        domainlist.set(domain_name_l)
        return domainlist


    @property
    def location_d(self):
        location_d = {}
        for host in self.__iter__():
            location = host.location.name
            if location not in location_d.keys():
                location_d[location] = HostList()
            location_d[location].append(host)
        return location_d

    def reconfigure(self):
        """
        reconfigure all Hosts in this list
        """
        # 1. create a file with the list of hostnames
        filename = '/tmp/hosts_reconfigure_%' %int(time.time())
        f = open(filename, 'w')

        # 2. add the hostnames to the file
        for host in self.__iter__():
            f.write('%s\n' %host.name)
        f.close()

        # 3. reconfigure
        cmd = 'aq --list %s' %filename
        results = run(cmd)

        # 4. delete the file
        os.remove(filename)

    def filter_by_personality(self, personality_l):
        """
        creates a new HostList object, with only the Hosts
        that belong to a given Personality
        """
        personality_name_l = [p.name for p in personality_l]

        newHostList = HostList()
        for host in self.__iter__():
            if host.personality.name in personality_name_l:
                newHostList.append(host)
        return newHostList

    def dump(self, path):
        """
        :param str path: path of the file to write the list of hostnames
        """
        with open(path, 'w') as f:
            for host in self.__iter__():
                name = host.name
                line = '%s\n' %name
                f.write(line)
