from lib.Logger import Logger
from lib.popen import subprocess_popen
from threading import Thread
import time


class Valve:
    def __init__(self):
        self.next = None
        self.is_first_valve = False
        self.metrics = []

        self.name = "New stage"
        self.description = ""
        self.isOnline = False

        self.concurrency = 1
        self.logger = Logger('./log/benchmark.log', 'stage')

    def set_next(self, next):
        self.next = next

    def set_first_stage(self):
        self.is_first_valve = True

    def run(self, context):
        threads = []
        for i in range(self.concurrency):
            threads.append(Thread(target=self.run_thread, args=(context, i)))
        self.logger.info("Starting threads...")
        for thread in threads:
            thread.start()
        self.logger.info("Waiting for all threads to finish...")
        for thread in threads:
            thread.join()
        self.logger.info("All threads finished!")
        self.logger.info("Stage finished!")
        self.logger.info("--------------------------------")

    def run_thread(self, context, thread_id):
        pass

    def get_metrics(self):
        return self.metrics


class OfflineStage(Valve):
    def __init__(self, config):
        super().__init__()
        self.logger = Logger('./log/benchmark.log', 'offline_stage')
        self.name = config['name']
        self.description = config['description']
        self.commands = config['commands']
        self.concurrency = config['concurrency']

    def run_thread(self, context, thread_id):
        for item in self.commands:
            try:
                command = 'cd ' + item['path'] + ' && ' + item['command']
            except KeyError:
                command = item['command']
            start = time.time()
            subprocess_popen(command)
            finish = time.time()
            summary = {'threadID': str(thread_id), 'command': command, 'start': start, 'finish': finish}
            self.metrics.append(summary)


class OnlineStage(Valve):
    def __init__(self, config):
        super().__init__()
        self.logger = Logger('./log/benchmark.log', 'online_stage')
        self.name = config['name']
        self.description = config['description']
        self.queries = config['queries']
        self.isOnline = True
        self.concurrency = config['concurrency']
        self.loop = config['loop']

    def run_thread(self, context, thread_id):
        context.engine.query(context.queries['database'])
        for i in range(self.loop):
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
                        summary = {'threadID': str(thread_id), 'query': query, 'start': start, 'finish': finish}
                        self.metrics.append(summary)
                        self.logger.info("Execution of " + query + " complete.")