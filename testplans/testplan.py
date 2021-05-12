from abc import ABCMeta, abstractmethod


class Testplan(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.pipeline = None
        self.latch = None

    @abstractmethod
    def build(self, conf):
        pass

    def start(self, engine, queries):
        self.pipeline.start(engine, queries)
        self.latch.call_latch()

    def get_metrics(self):
        return self.pipeline.get_metrics()