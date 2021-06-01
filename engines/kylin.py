from engines.engine import engine
import sqlalchemy as sa
import time


class kylin(engine):
    def __init__(self):
        super().__init__()
        self.kylin = None

    def launch(self):
        self.logger.info("Launching kylin...")
        self.kylin = sa.create_engine('kylin://ADMIN:KYLIN@localhost:7070/tpch?version=v1')
        self.logger.info("Launch kylin complete.")

    def query(self, sql):
        self.sql = sql
        start = time.time()
        results = self.kylin.execute(sql)
        end = time.time()
        if len(results) > 10:
            results = results[:10]
        for line in results:
            print(line)
        return end - start

    def stop(self):
        pass

    def set_conf(self, conf):
        pass
