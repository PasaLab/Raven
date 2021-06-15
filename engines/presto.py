from engines.engine import engine
import prestodb
import time


class presto(engine):
    def __init__(self):
        super().__init__()
        self.conn = None
        self.conf = {}

    def launch(self):
        self.logger.info("Launching presto...")
        self.conn = prestodb.dbapi.connect(
            host=self.conf['host'],
            port=self.conf['port'],
            catalog='hive',
            schema='default',
            user='hadoop',
        )
        self.logger.info("Launch presto complete.")

    def query(self, sql):
        self.sql = sql
        start = time.time()
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        print(rows)
        end = time.time()
        return end - start

    def stop(self):
        pass

    def set_conf(self, conf):
        for key, value in conf.items():
            self.conf[key] = value
