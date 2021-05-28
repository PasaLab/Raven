from testplans.testplan import Testplan
from pipeline.pipeline import Pipeline
from pipeline.valve import OfflineStage, OnlineStage


class One_offline_multi_online_testplan(Testplan):
    def __init__(self):
        pass

    def build(self, conf):
        self.pipeline = Pipeline()
        offline = OfflineStage(conf['offline'])
        onlines = []
        online_confs = conf['online']
        for online_conf in online_confs:
            onlines.append(OnlineStage(online_conf))
        offline.set_next(onlines[0])
        onlines[0].set_next(onlines[1])
        offline.set_first_stage()
        self.pipeline.add_stage(offline)
        self.pipeline.add_stage(onlines[0])
        self.pipeline.add_stage(onlines[1])
        return
