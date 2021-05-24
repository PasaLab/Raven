import json
import boto3
from lib.boto3sdk import download
from lib.Logger import Logger


def get_metrics(cid, start, end):
    ec2 = boto3.client('ec2',
                       region_name='ap-southeast-1',
                       aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                       aws_secret_access_key='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')
    reservations = ec2.describe_instances()
    responses = []
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            is_instance = False
            for tag in instance['Tags']:
                if tag['Key'] == 'aws:elasticmapreduce:job-flow-id':
                    if tag['Value'] == cid:
                        is_instance = True
            if is_instance:
                responses.append(get_metrics_from_cwa(instance, start, end))
    return responses


def get_metrics_from_cwa(instance, start, end):
    cw = boto3.client('cloudwatch',
                      region_name='ap-southeast-1',
                      aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                      aws_secret_access_key='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')

    with open('./cloud/metrics.json', 'r', encoding="utf-8") as f:
        metrics = json.load(f)
    for metric in metrics:
        metric['MetricStat']['Metric']['Dimensions'].append({
            'Name': 'InstanceId',
            'Value': instance['InstanceId']
        })
        metric['MetricStat']['Metric']['Dimensions'].append({
            'Name': 'ImageId',
            'Value': instance['ImageId']
        })
        metric['MetricStat']['Metric']['Dimensions'].append({
            'Name': 'InstanceType',
            'Value': instance['InstanceType']
        })
    response = cw.get_metric_data(
        StartTime=start - 30,
        EndTime=end + 30,
        MetricDataQueries=metrics
    )

    my_response = []
    for metric in response['MetricDataResults']:
        my_metric = {'Label': metric['Label'], 'Timestamps': [], 'Values': []}
        for timestamp in metric['Timestamps']:
            my_metric['Timestamps'].append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        for value in metric['Values']:
            my_metric['Values'].append(value)
        my_response.append(my_metric)
    return my_response


def analyze(metrics, timestamps):
    return 0


if __name__ == '__main__':
    logger = Logger('./log/benchmark.log', 'monitor')
    cluster_id = 'j-OVZ73NAH548A'
    m = get_metrics(cluster_id, 1621837574, 1621838170)
    t = {}
    download("olapstorage", "tmp/offline_times", "./offline_times")
    download("olapstorage", "tmp/online_times", "./online_times")
    with open("./offline_times", 'r', encoding='utf-8') as f:
        t['offline'] = f.read()
    with open("./online_times", 'r', encoding='utf-8') as f:
        t['online'] = f.read()
    score = analyze(m, t)
