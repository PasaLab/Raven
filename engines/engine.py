from abc import ABCMeta, abstractmethod
from lib.Logger import Logger


class engine(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.conf = None
        self.sql = None
        self.metrics = {}
        self.logger = Logger('./log/benchmark.log', 'engine')

    @abstractmethod
    def launch(self):
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
