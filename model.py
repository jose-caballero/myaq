import re

from sysadmin.myshell import run

# ==============================================================================
# NOTE: this class is under development / to be tested
# ==============================================================================
class ModelHandler(object):

    @property
    def models(self):
        """
        returns a ModelList with all Models currently in Aquilon
        """
        model_l = ModelList()
        cmd = 'aq show_model --all'
        results = run(cmd)
        for line in results.out.split('\n'):
            if line.startswith('Vendor') and 'Model' in line:
                # line is like this:
                # Vendor: clustervision Model: disk-2011-clustervision
                model_name = line.split()[-1]
                model = Model(model_name)
                model_l.append(model)
        return model_l


class Model(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    @property
    def hosts(self):
        from myaq.host import Host, HostList
        cmd = '/opt/aquilon/bin/aq.py search_host --model %s' %self.name
        results = run(cmd)
        host_l = HostList()
        for name in results.out.split():
            host = Host(name)
            host_l.append(host)
        return host_l

    @property
    def machines(self):
        from myaq.machine import Machine, MachineList
        cmd = '/opt/aquilon/bin/aq.py search_machine --model %s' %self.name
        results = run(cmd)
        machine_l = MachineList()
        for name in results.out.split():
            machine = Machine(name)
            machine_l.append(machine)
        return machine_l

    @property
    def year(self):
        """
        when possible, get the year from the Model name
        Usually, that is the case for Worker Nodes
        """
        try:
            year = self.name.split('-')[-2]
            if re.match('[0-9]{4}', year):
                return year
            else:
                return None
        except:
            return None

    def dump(self, path):
        """
        :param str path: path of the file to write the list of hostnames
        """
        with open(path, 'w') as f:
            for host in self.hosts:
                name = host.name
                line = '%s\n' %name
                f.write(line)


class ModelList(list):

    def __str__(self):
        out = ""
        for m in self.__iter__():
            out += str(m)
            out += '\n'
        return out

    def set(self, name_l):
        for name in name_l:
            self.append(Model(name))

    @property
    def hosts(self):
        from myaq.host import Host, HostList
        host_l = HostList()
        for model in self.__iter__():
            host_l += model.hosts
        return host_l

    def dump(self, path):
        """
        :param str path: path of the file to write the list of hostnames
        """
        with open(path, 'w') as f:
            for host in self.hosts:
                name = host.name
                line = '%s\n' %name
                f.write(line)
