from engines.engine import engine
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
import time


class sparksql(engine):
    def __init__(self):
        super().__init__()
        self.conf = SparkConf()
        self.session = None

    def launch(self):
        self.logger.info("Launching spark-sql...")
        self.session = SparkSession.builder\
            .config(conf=self.conf)\
            .enableHiveSupport()\
            .getOrCreate()
        self.logger.info("Launch spark-sql complete.")

    def query(self, sql):
        self.sql = sql
        if self.session is not None:
            start = time.time()
            self.session.sql(self.sql).show()
            end = time.time()
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
