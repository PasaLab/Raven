from abc import ABCMeta, abstractmethod


class engine(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.conf = None

    @abstractmethod
    def launch(self, internal_dns):
        pass

    @abstractmethod
    def query(self, sql):
        pass

    @abstractmethod
    def stop(self):
        pass

    def set_conf(self, conf):
        self.conf = conf

    def get_conf(self):
        return self.conf
