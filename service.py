from bcolors import bcolors
from sysadmin.myshell import run


class Service(object):
    def __init__(self, name, instance):
        self.name = name
        self.instance = instance
        self.info = None

    def __str__(self):
        """
        Human friendly representation of this Service
        """
        out = bcolors.WARNING + 'service:             ' + bcolors.ENDC + self.name
        if not self.info:
            self._show_service()
        instance_l =[]
        for line in self.info.split('\n'):
            line = line.strip()
            if 'Instance' in line:
                name = line.split()[-1]
                out += '\n' + bcolors.WARNING + '    instance:            ' + bcolors.ENDC + name
            if 'Server Binding' in line:
                name = line.split()[-1]
                out += '\n' + bcolors.WARNING + '    server:              ' + bcolors.ENDC + name
            if line.startswith('Client Count'):
                n = line.split()[-1]
                out += '\n' + bcolors.WARNING + '    clients:             ' + bcolors.ENDC + n
        out += '\n'
        return out

    def _show_service(self):
        cmd = "/opt/aquilon/bin/aq.py show_service --service %s" %self.name
        results = run(cmd)
        self.info = results.out
        return self.info

    @property
    def instances(self):
        if not self.info:
            self._show_service()
        instance_l =[]
        for line in self.info:
            line = line.strip()
            if 'Instance' in line:
                name = line.split()[-1]
                instance_l.append(line)
        return instance_l

    @property
    def hosts(self):
        """
        return the list of Host (as a HostList) included in this Service
        # FIXME
        # I don't think this method works. The command line is for single services only
        """
        from myaq.host import Host, HostList
        cmd = "/opt/aquilon/bin/aq.py search_host --service %s" %self.name
        results = run(cmd)
        # FIXME
        # check rt == 0, otherwise raise an Exception
        hostlist = HostList()
        for name in results.out.split():
            host = Host(name)
            hostlist.append(host)
        return hostlist

    def bind_host(self, host):
        """
        make a Host a provider of this Service
        """
        cmd = 'aq bind_server --service %s --instance %s --hostname %s' %(self.name, self.instance, host.name)
        results = run(cmd)

    def bind_cluster(self, cluster):
        """
        make a Cluster of Hosts a provider of this Service
        """
        cmd = 'aq bind_server --service %s --instance %s --cluster %s' %(self.name, self.instance, cluster.name)
        results = run(cmd)

    def unbind_host(self, host):
        """
        stop making a Host a provider of this Service
        """
        cmd = 'aq unbind_server --service %s --instance %s --hostname %s' %(self.name, self.instance, host.name)
        results = run(cmd)

    def unbind_cluster(self, cluster):
        """
        stop making a Cluster of Hosts a provider of this Service
        """
        cmd = 'aq unbind_server --service %s --instance %s --cluster %s' %(self.name, self.instance, cluster.name)
        results = run(cmd)
