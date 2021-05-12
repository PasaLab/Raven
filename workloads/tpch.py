from workloads.workload import workload
from lib.popen import subprocess_popen
from lib.Logger import Logger


class tpch(workload):
    def __init__(self):
        super().__init__()
        self.conf = None
        self.switch = None
        self.logger = Logger('./log/benchmark.log', __name__)

    def generate(self):
        command = 'cd ' + self.conf['generate']['path'] + ' && ' + self.conf['generate']['command']
        subprocess_popen(command)

    def create(self, engine):
        for sql in self.conf['create']['sql']:
            engine.query(sql)

    def load(self, engine):
        src = self.conf['load']['path']
        tables = self.conf['load']['tables']
        for table in tables:
            sql = "LOAD DATA INPATH '" + src + "/" + table['load'] + "' INTO TABLE " + table['as']
            engine.query(sql)
            self.logger.info("Successfully uploaded " + table['load'] + "as" + table['as'] + ".")

    def delete(self):
        pass

    def drop(self):
        pass

    def set_switch(self, switch):
        self.switch = switch

    def set_query(self, query):
        self.query = query

    def get_switch(self):
        return self.switch

    def get_query(self):
        return self.query