import json
import boto3
import yaml
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
            my_metric['Timestamps'].append(timestamp)
        for value in metric['Values']:
            my_metric['Values'].append(value)
        my_response.append(my_metric)
    return my_response


def analyze(metrics, timestamps, start, finish):
    global_conf_file = open("config/config.yaml", encoding="UTF-8")
    global_conf = yaml.load(global_conf_file, Loader=yaml.FullLoader)
    try:
        type = global_conf['metrics']
    except KeyError:
        logger.error("Failed: incomplete key-value pairs")
        return
    try:
        conf_file = open("config/metrics/" + global_conf['metrics'] + ".yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.error("Failed: invalid metrics type")
        return

    if 'time_tot_offline' in conf['metrics']:
        time_tot_offline = 0
        for command in timestamps['offline']:
            time_tot_offline += command['finish'] - command['start']
    if 'time_tot_online' in conf['metrics']:
        time_tot_online = 0
        for query in timestamps['online']:
            time_tot_online += query['finish'] - query['start']
    if 'time_avg_offline' in conf['metrics']:
        time_avg_offline = 0
        for command in timestamps['offline']:
            time_avg_offline += command['finish'] - command['start']
        time_avg_offline = time_avg_offline / len(timestamps['offline'])
    if 'time_avg_online' in conf['metrics']:
        time_avg_online = 0
        for query in timestamps['online']:
            time_avg_online += query['finish'] - query['start']
        time_avg_online = time_avg_online / len(timestamps['online'])
    if 'cpu_avg_online' in conf['metrics']:
        cpu_avg_online = 0
        cpu_avg_online_cnt = 0
        for instance in metrics:
            for metric in instance:
                if metric['Label'] == "cpu_usage_user":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            cpu_avg_online = metric['Values'][i]
                            cpu_avg_online_cnt += 1
        cpu_avg_online = cpu_avg_online / cpu_avg_online_cnt * 0.01
    if 'mem_avg_online' in conf['metrics']:
        mem_avg_online = 0
        mem_avg_online_cnt = 0
        for instance in metrics:
            for metric in instance:
                if metric['Label'] == "mem_used_percent":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            mem_avg_online = metric['Values'][i]
                            mem_avg_online_cnt += 1
        mem_avg_online = mem_avg_online / mem_avg_online_cnt * 0.01

    offline_calculation_overhead = eval(str(conf['offline']['calculation']['eval']))
    offline_delay_overhead = eval(str(conf['offline']['delay']['eval']))
    online_calculation_overhead = eval(str(conf['online']['calculation']['eval']))
    online_delay_overhead = eval(str(conf['online']['delay']['eval']))
    logger.info("--------------------------------")
    logger.info("Offline calculation overhead: " + str(round(offline_calculation_overhead, 3)))
    logger.info("Offline delay overhead: " + str(round(offline_delay_overhead, 3)))
    logger.info("--------------------------------")
    logger.info("Online calculation overhead: " + str(round(online_calculation_overhead, 3)))
    logger.info("Online delay overhead: " + str(round(online_delay_overhead, 3)))
    logger.info("--------------------------------")
    overhead = eval(str(conf['total']['eval']))
    logger.info("Total overhead: " + str(round(overhead, 3)))
    return overhead


if __name__ == '__main__':
    logger = Logger('./log/benchmark.log', 'monitor')
    cluster_id = 'j-OVZ73NAH548A'
    start = 1621838460
    finish = 1621839025
    m = get_metrics(cluster_id, start, finish)
    #with open("./metrics", 'a', encoding='utf-8') as f:
    #    print(m, file=f)
    download("olapstorage", "tmp/offline_times", "./offline_times")
    download("olapstorage", "tmp/online_times", "./online_times")
    #with open("./metrics", 'r', encoding='utf-8') as f:
    #    m = json.loads(f.read().replace("'","\""))
    t = {}
    with open("./offline_times", 'r', encoding='utf-8') as f:
        t['offline'] = json.loads(f.read().replace("'","\""))
    with open("./online_times", 'r', encoding='utf-8') as f:
        t['online'] = json.loads(f.read().replace("'","\""))
    score = analyze(m, t, start, finish)
    logger.info("--------------------------------")
    logger.info("Benchmark finished.")
    logger.info("--------------------------------")