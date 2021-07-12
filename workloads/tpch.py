from workloads.workload import workload
from pyhive import hive
from lib.boto3sdk import upload, download
from lib.Logger import Logger
from lib.popen import subprocess_popen


class tpch(workload):
    def __init__(self):
        super().__init__()
        self.conf = None
        self.switch = None
        self.query = []
        self.logger = Logger('./log/benchmark.log', __name__)

    def generate(self):
        subprocess_popen("cd " + self.conf['generate']['path'] + " && " + self.conf['generate']['command'])
        for file in self.conf['generate']['files']:
            upload(self.conf['generate']['path'] + "/" + file, "olapstorage", "tpch/" + file)

    def create(self):
        hive_conn = hive.Connection(host=self.conf['host'], port=10000, username='hadoop',
                                    database=self.conf['database'])
        cursor = hive_conn.cursor()
        for sql in self.conf['create']['sql']:
            cursor.execute(sql)

    def load(self):
        hive_conn = hive.Connection(host=self.conf['host'], port=10000, username='hadoop',
                                    database=self.conf['database'])
        cursor = hive_conn.cursor()
        for table in self.conf['load']['tables']:
            download("olapstorage", "tpch/" + table['load'], "./" + table['load'])
        for table in self.conf['load']['tables']:
            sql = "LOAD DATA LOCAL INPATH './" + table['load'] + "' INTO TABLE " + table['as']
            cursor.execute(sql)
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
