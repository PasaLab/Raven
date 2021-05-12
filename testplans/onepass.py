from testplans.testplan import Testplan
from pipeline.pipeline import Pipeline
from pipeline.valve import OfflineStage, OnlineStage


class One_pass_testplan(Testplan):
    def __init__(self):
        pass

    def build(self, conf):
        self.pipeline = Pipeline()
        offline = OfflineStage(conf['offline'])
        online = OnlineStage(conf['online'])
        offline.set_next(online)
        offline.set_first_stage()
        self.pipeline.add_stage(offline)
        self.pipeline.add_stage(online)
        return
