import boto3


def upload(local_path, remote_bucket, remote_path):
    s3 = boto3.client('s3',
                      region_name='ap-southeast-1',
                      aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                      aws_secret_access_key='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')
    s3.upload_file(local_path, remote_bucket, remote_path)
    return 0
    # usage: upload("./test.txt", "olapstorage", "workload/tpch/test")


def download(remote_bucket, remote_path, local_path):
    s3 = boto3.client('s3',
                      region_name='ap-southeast-1',
                      aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                      aws_secret_access_key='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')
    s3.download_file(remote_bucket, remote_path, local_path)
    return 0
    # usage: download("olapstorage", "workload/tpch/test", "./test.txt")