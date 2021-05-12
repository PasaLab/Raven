from testplans.testplan import Testplan
from pipeline.pipeline import Pipeline
from pipeline.latch import Latch
from pipeline.valve import OfflineStage, OnlineStage


class One_pass_testplan(Testplan):
    def __init__(self):
        pass

    def build(self, conf):
        self.pipeline = Pipeline()
        self.latch = Latch(0, 1)
        self.pipeline.set_latch(self.latch)
        offline = OfflineStage(conf['offline'])
        online = OnlineStage(conf['online'])
        offline.set_next(online)
        offline.set_first_stage()
        self.pipeline.add_stage(offline)
        self.pipeline.add_stage(online)
        return
