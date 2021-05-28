from workloads.workload import workload
from lib.boto3sdk import upload, download
from lib.Logger import Logger
from lib.popen import subprocess_popen

class tpch(workload):
    def __init__(self):
        super().__init__()
        self.conf = None
        self.switch = None
        self.logger = Logger('./log/benchmark.log', __name__)

    def generate(self):
        subprocess_popen("cd " + self.conf['generate']['path'] + " && " + self.conf['generate']['command'])
        for file in self.conf['generate']['files']:
            upload(self.conf['generate']['path'] + "/" + file, "olapstorage", "tpch/" + file)

    def create(self, engine):
        for sql in self.conf['create']['sql']:
            engine.query(sql)

    def load(self, engine):
        tables = self.conf['load']['tables']
        for table in tables:
            download("olapstorage", "tpch/" + table['load'], "./" + table['load'])
        for table in tables:
            sql = "LOAD DATA LOCAL INPATH './" + table['load'] + "' INTO TABLE " + table['as']
            engine.query(sql)
            self.logger.info("Successfully uploaded " + table['load'] + " as " + table['as'] + ".")

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
