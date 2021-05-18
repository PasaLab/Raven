import time
import boto3
from lib.Logger import Logger
from lib.popen import subprocess_popen


def prepare():
    # 0. Initialize boto3 clients
    emr = boto3.client('emr',
                       region_name='ap-southeast-1',
                       aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                       aws_secret_access_key='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')
    ec2 = boto3.client('ec2',
                       region_name='ap-southeast-1',
                       aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                       aws_secret_access_key='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')

    # 1. Create an EMR cluster on AWS
    logger.info("Creating the EMR cluster...")
    with open("./cloud/cluster.sh", 'r') as f:
        cmd = f.read()
        res = subprocess_popen(cmd)
    cid = res[1][res[1].find("j-"):len(res[1])-2]
    logger.info("Cluster created! Cluster ID is " + cid + ".")

    # 2. Check if all EC2 instances are ready
    logger.info("Creating EC2 instances for the cluster...")
    found_flag = False
    while found_flag is False:
        time.sleep(15)
        masters = []
        cores = []
        masters_to_find = 1
        cores_to_find = 2
        reservations = ec2.describe_instances()
        for reservation in reservations['Reservations']:
            for instance in reservation['Instances']:
                is_instance = False
                for tag in instance['Tags']:
                    if tag['Key'] == 'aws:elasticmapreduce:job-flow-id':
                        if tag['Value'] == cid:
                            is_instance = True
                if is_instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'aws:elasticmapreduce:instance-group-role':
                            if tag['Value'] == 'MASTER':
                                masters.append(instance)
                            else:
                                cores.append(instance)
        if len(masters) == masters_to_find and len(cores) == cores_to_find:
            found_flag = True
        else:
            logger.info("MASTERs to create: " + str(masters_to_find - len(masters)) + ", "
                        + "COREs to create: " + str(cores_to_find - len(cores)) + ".")
    logger.info("All instances are created! Starting cluster...")
    logger.info("It may take up to 10 minutes to start a cluster.")

    started_flag = False
    while started_flag is False:
        time.sleep(55)
        clusters = emr.list_clusters()
        for cluster in clusters['Clusters']:
            if cluster['Id'] == cid:
                if cluster['Status']['State'] == 'WAITING':
                    started_flag = True
                else:
                    logger.info("Cluster starting, please wait...")
                    break
    logger.info("Cluster started!")
    return cid


def get_metrics(cid):
    ec2 = boto3.client('ec2',
                       region_name='ap-southeast-1',
                       aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                       aws_secret_access_key='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')
    reservations = ec2.describe_instances()
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            is_instance = False
            for tag in instance['Tags']:
                if tag['Key'] == 'aws:elasticmapreduce:job-flow-id':
                    if tag['Value'] == cid:
                        is_instance = True
            if is_instance:
                get_metrics_from_cwa(instance)


def get_metrics_from_cwa(instance):
    cw = boto3.client('cloudwatch',
                      region_name='ap-southeast-1',
                      aws_access_key_id='AKIASNVXWRHNSSQ3M2AA',
                      aws_secret_access_key='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')
    t = time.time()
    response = cw.get_metric_data(
        StartTime=int(t) - 3600,
        EndTime=int(t) - 0,
        MetricDataQueries=[
            {
                "Id": "m1",
                "Label": "cpu_usage_user",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "CWAgent",
                        "MetricName": "cpu_usage_user",
                        "Dimensions": [
                            {
                                "Name": "InstanceId",
                                "Value": instance['InstanceId']
                            },
                            {
                                "Name": "ImageId",
                                "Value": instance['ImageId']
                            },
                            {
                                "Name": "InstanceType",
                                "Value": instance['InstanceType']
                            },
                            {
                                "Name": "cpu",
                                "Value": "cpu0"
                            }
                        ]
                    },
                    "Period": 10,
                    "Stat": "Average"
                }
            },
            {
                "Id": "m2",
                "Label": "mem_used_percent",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "CWAgent",
                        "MetricName": "mem_used_percent",
                        "Dimensions": [
                            {
                                "Name": "InstanceId",
                                "Value": instance['InstanceId']
                            },
                            {
                                "Name": "ImageId",
                                "Value": instance['ImageId']
                            },
                            {
                                "Name": "InstanceType",
                                "Value": instance['InstanceType']
                            }
                        ]
                    },
                    "Period": 10,
                    "Stat": "Average"
                }
            },
        ],
    )

    my_response = []
    for metric in response['MetricDataResults']:
        my_metric = {'Label': metric['Label'], 'Timestamps': [], 'Values': []}
        for timestamp in metric['Timestamps']:
            my_metric['Timestamps'].append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        for value in metric['Values']:
            my_metric['Values'].append(value)
        my_response.append(my_metric)
    for metric in my_response:
        logger.info(metric['Label'])
        logger.info(metric['Timestamps'])
        logger.info(metric['Values'])


if __name__ == '__main__':
    logger = Logger('./log/benchmark.log', 'monitor')
    cluster_id = prepare()
    # get_metrics(cluster_id)
