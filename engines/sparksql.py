from engines.engine import engine
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from lib.Logger import Logger
import time


class sparksql(engine):
    def __init__(self):
        super().__init__()
        self.conf = SparkConf()
        self.session = None
        self.sql = None
        self.metrics = {}

    def launch(self):
        # initialize logger
        logger = Logger('./log/benchmark.log', 'engine')
        logger.info("Launching spark-sql...")
        self.session = SparkSession.builder\
            .config(conf=self.conf)\
            .enableHiveSupport()\
            .getOrCreate()
        logger.info("Launch spark-sql complete.")

    def query(self, sql):
        # initialize logger
        logger = Logger('./log/benchmark.log')
        self.sql = sql
        if self.session is not None:
            start = time.time()
            df = self.session.sql(self.sql).show()
            end = time.time()
            logger.info("Success: execution complete")
            return end - start
        else:
            logger.info("Failed on query: no session available.")
            return -1

    def stop(self):
        SparkSession.stop()
        self.session = None

    def set_app_name(self, name):
        self.conf.setAppName(name)

    def set_conf(self, conf):
        for key, value in conf.items():
            self.conf.set(key, value)
