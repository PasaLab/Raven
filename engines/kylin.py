from engines.engine import engine
import json
import time
import requests


class kylin(engine):
    def __init__(self):
        super().__init__()
        self.kylin = None

    def launch(self):
        self.logger.info("Launching kylin...")
        self.logger.info('Kylin has been launched manually by the user.')
        self.logger.info("Launch kylin complete.")

    def query(self, sql):
        self.sql = sql
        url = "http://localhost:7070/kylin/api/query"
        payload = {
            'sql': self.sql,
            'offset': 0,
            'limit': 20,
            'acceptPartial': True,
            'project': 'tpch',
            'backdoorToggles': None
        }
        payload = json.dumps(payload)
        headers = {
            'Authorization': "Basic QURNSU46S1lMSU4=",
            'content-type': "application/json;charset=UTF-8",
        }
        start = time.time()
        response = requests.request("POST", url, data=payload, headers=headers)
        end = time.time()
        message = json.loads(response.text)
        for result in message['results']:
            first_cell = True
            for cell in result:
                if first_cell:
                    print(cell, end="")
                    first_cell = False
                else:
                    print("\t" + cell, end="")
            print("")
        return end - start

    def stop(self):
        pass

    def set_conf(self, conf):
        pass
