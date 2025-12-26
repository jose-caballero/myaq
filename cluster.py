from bcolors import bcolors
from sysadmin.myshell import run


class Cluster(object):
    def __init__(self, name):
        self.name = name
        self.info = None

    def __str__(self):
        """
        Human friendly representation of this Cluster
        """
        out = ""
        out += '\n' + bcolors.WARNING + 'cluster name:     ' + bcolors.ENDC + self.name
        hosts = self.hosts
        if hosts[0].location.category == "Domain":
            out += '\n' + bcolors.WARNING + 'domain:           ' + bcolors.ENDC + hosts[0].location.name
        if hosts[0].location.category == "Sandbox":
            out += '\n' + bcolors.WARNING + 'sandbox:          ' + bcolors.ENDC + hosts[0].location.name
        out += '\n' + bcolors.WARNING + 'Hosts:            ' + bcolors.ENDC + hosts[0].name
        for host in hosts[1:]:
            out += '\n' + '                  ' + host.name
        if self.service:
            out += '\n' + bcolors.WARNING + 'service/instance: ' + bcolors.ENDC + self.service.name + ' / ' + self.service.instance
        out += "\n"
        return out

    def _show_cluster(self):
        cmd = "/opt/aquilon/bin/aq.py show_cluster --cluster %s" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info

    @property
    def hosts(self):
        """
        return the list of Host (as a HostList) included in this Cluster
        """
        from myaq.host import Host, HostList
        hostlist = HostList()
        if not self.info:
            self._show_cluster()
        for line in self.info.split('\n'):
            if 'Member:' in line:
                name = line.split()[1].strip()
                host = Host(name)
                hostlist.append(host)
        return hostlist

    @property
    def service(self):
        """
        get the Service for this Host
        """
        from myaq.service import Service
        if not self.info:
            self._show_cluster()
        for line in self.info.split('\n'):
            if 'Provides Service' in line:
                service = line.split()[2].strip()
                instance = line.split()[-1].strip()
                return Service(service, instance)
        else:
            # The Host is not part of any Service
            return None

    def add_host(self, host):
        cmd = "/opt/aquilon/bin/aq.py cluster --hostname %s --cluster %s" %(host.name, self.name)
        results = run(cmd)
        self.info = results.out
        return self.info

    def remove_host(self, host):
        cmd = "/opt/aquilon/bin/aq.py uncluster --hostname %s --cluster %s" %(host.name, self.name)
        results = run(cmd)
        self.info = results.out
        return self.info

    def remove(self):
        """
        delete this cluster
        """
        cmd = "/opt/aquilon/bin/aq.py del_cluster --cluster %s" %self.name
        results = run(cmd)
        return results

