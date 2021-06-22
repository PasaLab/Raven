from engines.engine import engine
import prestodb
import time


class presto(engine):
    def __init__(self):
        super().__init__()
        self.conn = None
        self.conf = {
            'host': 'localhost',
            'port': '8889'
        }

    def launch(self):
        self.logger.info("Launching presto...")
        self.conn = prestodb.dbapi.connect(
            host=self.conf['host'],
            port=self.conf['port'],
            catalog='hive',
            schema='tpch_flat_orc_2',
            user='hadoop'
        )
        self.logger.info("Launch presto complete.")

    def query(self, sql):
        self.sql = sql.rstrip(';')
        start = time.time()
        cur = self.conn.cursor()
        cur.execute(self.sql)
        rows = cur.fetchall()
        end = time.time()
        return end - start

    def stop(self):
        pass

    def set_conf(self, conf):
        for key, value in conf.items():
            self.conf.setdefault(key, value)
