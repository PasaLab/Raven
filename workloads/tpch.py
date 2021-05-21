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
        commands = self.conf['generate']['commands']
        command_seq = ""
        command_first = True
        for command in commands:
            if command_first:
                command_seq = command_seq + command
                command_first = False
            else:
                command_seq = command_seq + " && " + command
        subprocess_popen(command_seq)

    def create(self, engine):
        for sql in self.conf['create']['sql']:
            engine.query(sql)

    def load(self, engine):
        pre_command = self.conf['load']['pre_command']
        subprocess_popen(pre_command)
        tables = self.conf['load']['tables']
        for table in tables:
            sql = "LOAD DATA LOCAL INPATH './" + table['load'] + "' INTO TABLE " + table['as']
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