from sysadmin.myshell import run


class Vendor(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
