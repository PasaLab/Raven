from abc import ABCMeta, abstractmethod

class workload(object):
    __metaclass__ = ABCMeta
    def __init__(self):
        self.conf = None
        pass

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def drop(self):
        pass

    def set_conf(self, conf):
        self.conf = conf

    def get_conf(self):
        return self.conf