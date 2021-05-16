from engines.engine import engine
from pyspark.sql import SparkSession
from lib.Logger import Logger
import time


class sparksql(engine):
    def __init__(self):
        super().__init__()
        self.session = None
        self.sql = None
        self.metrics = {}
        self.logger = Logger('./log/benchmark.log', 'engine')

    def launch(self, internal_dns):
        self.logger.info("Launching spark-sql...")
        self.session = SparkSession.builder\
            .master("yarn")\
            .config("hive.metastore.uris", "thrift://" + internal_dns + ":9083")\
            .config("spark.sql.warehouse.dir", "hdfs://" + internal_dns + ":8020/user/hive/warehouse")\
            .enableHiveSupport()\
            .getOrCreate()
        self.session = SparkSession.builder\
            .config()\
            .enableHiveSupport()\
            .getOrCreate()
        self.logger.info("Launch spark-sql complete.")

    def query(self, sql):
        self.sql = sql
        if self.session is not None:
            start = time.time()
            self.session.sql(self.sql).show()
            end = time.time()
            self.logger.info("Success: execution complete")
            return end - start
        else:
            self.logger.info("Failed on query: no session available.")
            return -1

    def stop(self):
        SparkSession.stop()
        self.session = None

    def set_app_name(self, name):
        self.conf.setAppName(name)

    def set_conf(self, conf):
        for key, value in conf.items():
            self.conf.set(key, value)
