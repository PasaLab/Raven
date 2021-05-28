from lib.Logger import Logger
from lib.popen import subprocess_popen
from pipeline.metrics import Metrics
from threading import Thread
import time


class Valve:
    def __init__(self):
        self.next = None
        self.is_first_valve = False
        self.metrics = Metrics()

        self.name = "New stage"
        self.description = ""
        self.isOnline = False

        self.concurrent = False
        self.logger = Logger('./log/benchmark.log', 'stage')

    def set_next(self, next):
        self.next = next

    def set_first_stage(self):
        self.is_first_valve = True

    def run(self, context):
        if self.concurrent:
            threads = []
            for i in range(self.concurrent):
                threads.append(Thread(target=self.run_thread, args=(context,)))
            for thread in threads:
                thread.start()
        else:
            self.run_thread(context)

    def run_thread(self, context):
        pass

    def get_metrics(self):
        return self.metrics.get_metrics()


class OfflineStage(Valve):
    def __init__(self, config):
        super().__init__()
        self.name = config['name']
        self.description = config['description']
        self.commands = config['commands']
        if config['concurrency'] > 1:
            self.concurrent = True

    def run_thread(self, context):
        for item in self.commands:
            try:
                command = 'cd ' + item['path'] + ' && ' + item['command']
            except KeyError:
                command = item['command']
            start = time.time()
            subprocess_popen(command)
            finish = time.time()
            summary = {'command': command, 'start': start, 'finish': finish}
            self.metrics.set_metrics(summary)


class OnlineStage(Valve):
    def __init__(self, config):
        super().__init__()
        self.name = config['name']
        self.description = config['description']
        self.queries = config['queries']
        self.isOnline = True
        if config['concurrency'] > 1:
            self.concurrent = True

    def run_thread(self, context):
        for query in self.queries:
            for matching_query in context.queries['sql']:
                if matching_query['name'] == query:
                    sql = matching_query['sql']
                    start = time.time()
                    if sql == 'sqls':
                        sqls = matching_query['sqls']
                        for sql in sqls:
                            context.engine.query(sql)
                    else:
                        context.engine.query(sql)
                    finish = time.time()
                    summary = {'query': query, 'start': start, 'finish': finish}
                    self.metrics.set_metrics(summary)
                    self.logger.info("Execution of " + query + " complete.")
