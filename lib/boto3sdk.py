import boto3


def upload(local_path, remote_bucket, remote_path):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, remote_bucket, remote_path)
    return 0
    # usage: upload("./test.txt", "olapstorage", "workload/tpch/test")


def download(remote_bucket, remote_path, local_path):
    s3 = boto3.client('s3')
    s3.download_file(remote_bucket, remote_path, local_path)
    return 0
    # usage: download("olapstorage", "workload/tpch/test", "./test.txt")
