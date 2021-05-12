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
        command = 'cd ' + self.conf['generate']['path'] + ' && ' + self.conf['generate']['command']
        subprocess_popen(command)

    def create(self, engine):
        for sql in self.conf['create']['sql']:
            engine.query(sql)

    def upload(self):
        if self.conf['upload']['to'] == 'hdfs':
            src = self.conf['upload']['path']
            files = self.conf['upload']['files']
            command = 'hadoop fs -mkdir -p /tpch'
            subprocess_popen(command)
            for file in files:
                command = 'hadoop fs -moveFromLocal ' + src + '/' + file + ' /tpch'
                subprocess_popen(command)
        elif self.conf['upload']['to'] == 's3':
            src = self.conf['upload']['path']
            files = self.conf['upload']['files']
            import boto3
            from botocore.config import Config
            from botocore.exceptions import SSLError
            s3 = boto3.client('s3',
                              region_name='ap-southeast-1',
                              aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                              aws_secret_access_key='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',
                              config=Config(proxies={
                                  'http': '192.168.100.1:1081',
                                  'https': '192.168.100.1:1081'
                              }))
            bucket = self.conf['upload']['bucket']
            bucket_path = self.conf['upload']['bucket_path']
            for file in files:
                self.logger.info("Uploading " + file + " to s3...")
                try:
                    response = s3.upload_file(src + '/' + file, bucket, bucket_path + '/' + file)
                    self.logger.info("Successfully uploaded " + file + ".")
                except SSLError as e:
                    self.logger.error(str(e))
                    self.logger.error("Uploading " + file + " failed.")

    def load(self, engine):
        for sql in self.conf['load']['sql']:
            engine.query(sql)

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