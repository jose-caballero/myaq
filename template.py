import os

class Template(object):
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(self.path)

    @property
    def exists(self):
        return os.path.isfile(self.path)

    def initiate(self):
        f = open(self.path, 'w')
        if self.filename == 'config.pan':
            # FIXME !!
            #line = 'template %s' %...
            #f.write(line)
        else
            # FIXME !!
            #line = 'unique template %s' %...
            #f.write(line)


class TemplateList(list):

    def initiate(self):
        for t in self.__iter__():
            t.initiate()


        


