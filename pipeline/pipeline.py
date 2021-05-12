from pipeline.context import Context
from lib.Logger import Logger


class Pipeline:
    def __init__(self):
        self.context = Context()
        self.valves = []

    def add_stage(self, valve):
        self.valves.append(valve)

    def start(self, engine, queries):
        self.context.setEngine(engine)
        self.context.setQueries(queries)
        if len(self.valves) == 0:
            # initialize logger
            logger = Logger('./log/benchmark.log')
            logger.error("No valves available!")
        else:
            self.context.call(self.valves[self.get_first_valve_id()])

    def get_first_valve_id(self):
        for i, valve in enumerate(self.valves):
            if valve.is_first_valve is True:
                return i
        return 0

    def get_metrics(self):
        offline_metrics = []
        online_metrics = []
        for valve in self.valves:
            if valve.isOnline is True:
                online_metrics.append(valve.get_metrics())
            else:
                offline_metrics.append(valve.get_metrics())
        return offline_metrics, online_metrics
