import json
import boto3
import yaml
import numpy as np
import sys
from lib.Logger import Logger
import time


def get_metrics(cid, start, end):
    ec2 = boto3.client('ec2')
    reservations = ec2.describe_instances()
    responses = []
    for reservation in reservations['Reservations']:
        for instance in reservation['Instances']:
            is_instance = False
            try:
                for tag in instance['Tags']:
                    if tag['Key'] == 'aws:elasticmapreduce:job-flow-id':
                        if tag['Value'] == cid:
                            is_instance = True
                if is_instance:
                    responses.append(get_metrics_from_cwa(instance, start, end))
            except KeyError:
                pass
    return responses


def get_metrics_from_cwa(instance, start, end):
    cw = boto3.client('cloudwatch')

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
            my_metric['Timestamps'].append(timestamp.timestamp())
        for value in metric['Values']:
            my_metric['Values'].append(value)
        my_response.append(my_metric)
    return my_response


def analyze(metrics, timestamps):
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

    offline_times = []
    for command in timestamps['offline']:
        offline_times.append(command['finish'] - command['start'])
    online_times = []
    for query in timestamps['online']:
        online_times.append(query['finish'] - query['start'])

    # A. time-related metrics
    # A1. overall query speed
    if 'time_tot_offline' in conf['metrics']:
        time_tot_offline = np.sum(offline_times)
    if 'time_tot_online' in conf['metrics']:
        time_tot_online = np.sum(online_times)
    if 'time_avg_offline' in conf['metrics']:
        time_avg_offline = np.average(offline_times)
    if 'time_avg_online' in conf['metrics'] or 'queries_per_second' in conf['metrics']:
        time_avg_online = np.average(online_times)
        queries_per_second = 1.0 / time_avg_online

    # A2. query bottlenecks
    if 'time_max_online' in conf['metrics']:
        time_max_online = np.max(online_times)
    if 'time_99th_quantile' in conf['metrics'] or 'time_95th_quantile' in conf['metrics']\
            or 'time_90th_quantile' in conf['metrics'] or 'time_median_online' in conf['metrics']:
        time_99th_quantile = np.percentile(online_times, 99)
        time_95th_quantile = np.percentile(online_times, 95)
        time_90th_quantile = np.percentile(online_times, 90)
        time_median_online = np.percentile(online_times, 50)

    # A3. Query time distribution
    if 'time_between_queries' in conf['metrics']:
        temp_time_tot_online = 0
        temp_query_start = 0
        temp_query_finish = 0
        for query in timestamps['online']:
            if query['finish'] > temp_query_finish:
                temp_query_finish = query['finish']
            if query['start'] < temp_query_start or temp_query_start == 0:
                temp_query_start = query['start']
            temp_time_tot_online += query['finish'] - query['start']
        time_between_queries = temp_query_finish - temp_query_start - temp_time_tot_online
    if 'time_variation_per_query' in conf['metrics']:
        time_variation_per_query = np.std(online_times)

    # A4. Accordance for concurrent jobs
    pass

    # B. Resource Usage
    # B1. used resources & free time
    if 'cpu_avg_online' in conf['metrics'] or 'cpu_free_time' in conf['metrics']:
        temp_cpu_avg_online = 0
        temp_cpu_avg_online_cnt = 0
        for instance in metrics:
            for metric in instance:
                if metric['Label'] == "cpu_usage_user":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            temp_cpu_avg_online += metric['Values'][i]
                            temp_cpu_avg_online_cnt += 1
        cpu_avg_online = temp_cpu_avg_online / temp_cpu_avg_online_cnt * 0.01
        cpu_free_time = (finish - start) * (1 - cpu_avg_online)
    if 'mem_avg_online' in conf['metrics'] or 'mem_free_time' in conf['metrics']:
        temp_mem_avg_online = 0
        temp_mem_avg_online_cnt = 0
        for instance in metrics:
            for metric in instance:
                if metric['Label'] == "mem_used_percent":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            temp_mem_avg_online += metric['Values'][i]
                            temp_mem_avg_online_cnt += 1
        mem_avg_online = temp_mem_avg_online / temp_mem_avg_online_cnt * 0.01
        mem_free_time = (finish - start) * (1 - mem_avg_online)

    # B2. Load balance
    if 'cpu_load_balance' in conf['metrics']:
        temp_cpu_average_loads = []
        for instance in metrics:
            temp_cpu_avg_online = 0
            temp_cpu_avg_online_cnt = 0
            for metric in instance:
                if metric['Label'] == "cpu_usage_user":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            temp_cpu_avg_online += metric['Values'][i]
                            temp_cpu_avg_online_cnt += 1
            temp_cpu_average_loads.append(temp_cpu_avg_online / temp_cpu_avg_online_cnt * 0.01)
        cpu_load_balance = np.std(temp_cpu_average_loads)

    if 'mem_load_balance' in conf['metrics']:
        temp_mem_average_loads = []
        for instance in metrics:
            temp_mem_avg_online = 0
            temp_mem_avg_online_cnt = 0
            for metric in instance:
                if metric['Label'] == "mem_used_percent":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            temp_mem_avg_online += metric['Values'][i]
                            temp_mem_avg_online_cnt += 1
            temp_mem_average_loads.append(temp_mem_avg_online / temp_mem_avg_online_cnt * 0.01)
        mem_load_balance = np.std(temp_mem_average_loads)

    # B3. I/O efficiency
    if 'io_avg_time' in conf['metrics']:
        temp_io_avg_time = 0
        temp_io_avg_online_cnt = 0
        for instance in metrics:
            for metric in instance:
                if metric['Label'] == "io_time":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            temp_io_avg_time += metric['Values'][i]
                            temp_io_avg_online_cnt += 1
        io_avg_time = temp_io_avg_time / temp_io_avg_online_cnt * 0.01

    if 'disk_usage' in conf['metrics']:
        temp_disk_usage = 0
        temp_disk_usage_cnt = 0
        for instance in metrics:
            for metric in instance:
                if metric['Label'] == "disk_used":
                    for i in range(len(metric['Timestamps'])):
                        time = metric['Timestamps'][i]
                        if start <= time <= finish:
                            temp_disk_usage += metric['Values'][i]
                            temp_disk_usage_cnt += 1
        disk_usage = temp_disk_usage / temp_disk_usage_cnt * 0.01

    # C. Bill prediction

    offline_calculation_overhead = eval(str(conf['offline']['calculation']['eval']))
    offline_delay_overhead = eval(str(conf['offline']['delay']['eval']))
    online_calculation_overhead = eval(str(conf['online']['calculation']['eval']))
    online_delay_overhead = eval(str(conf['online']['delay']['eval']))
    # name = np.array(['Offline calculation', 'Offline delay', 'Online calculation', 'Online delay'])
    # value = np.array([offline_calculation_overhead, offline_delay_overhead, online_calculation_overhead, online_delay_overhead])
    # theta = np.concatenate((theta, [theta[0]]))
    # value = np.concatenate((value, [value[0]]))
    # name = np.array(['CPU idle', 'Memory idle', 'CPU skew', 'Memory skew'])
    # theta = np.linspace(0, 2 * np.pi, len(name), endpoint=False)
    # value = np.array([1 - cpu_avg_online, 1 - mem_avg_online, cpu_load_balance, mem_load_balance])
    # ax = plt.subplot(111, projection='polar')
    # ax.plot(theta, value, 'm-', lw=1, alpha=0.75)
    # ax.fill(theta, value, 'm', alpha=0.75)
    # ax.set_thetagrids(theta * 180 / np.pi, name)
    # ax.set_theta_zero_location('N')
    # ax.set_ylim(0,1)
    # ax.set_title('Benchmark Results - resources', fontsize=20)
    # plt.show()
    logger.debug("--------------------------------")
    if 'time_tot_offline' in conf['metrics']:
        logger.debug("time_tot_offline: " + str(time_tot_offline))
    if 'time_tot_online' in conf['metrics']:
        logger.debug("time_tot_online: " + str(time_tot_online))
    if 'time_avg_offline' in conf['metrics']:
        logger.debug("time_avg_offline: " + str(time_avg_offline))
    if 'time_avg_online' in conf['metrics'] or 'queries_per_second' in conf['metrics']:
        logger.debug("time_avg_online: " + str(time_avg_online))
        logger.debug("queries_per_second: " + str(queries_per_second))
    if 'time_max_online' in conf['metrics']:
        logger.debug("time_max_online: " + str(time_max_online))
    if 'time_99th_quantile' in conf['metrics'] or 'time_95th_quantile' in conf['metrics']\
            or 'time_90th_quantile' in conf['metrics'] or 'time_median_online' in conf['metrics']:
        logger.debug("time_99th_quantile: " + str(time_99th_quantile))
        logger.debug("time_95th_quantile: " + str(time_95th_quantile))
        logger.debug("time_90th_quantile: " + str(time_90th_quantile))
        logger.debug("time_median_online: " + str(time_median_online))
    if 'time_between_queries' in conf['metrics']:
        logger.debug("time_between_queries: " + str(time_between_queries))
    if 'time_variation_per_query' in conf['metrics']:
        logger.debug("time_variation_per_query: " + str(time_variation_per_query))
    if 'cpu_avg_online' in conf['metrics'] or 'cpu_free_time' in conf['metrics']:
        logger.debug("cpu_avg_online: " + str(cpu_avg_online))
        logger.debug("cpu_free_time: " + str(cpu_free_time))
    if 'mem_avg_online' in conf['metrics'] or 'mem_free_time' in conf['metrics']:
        logger.debug("mem_avg_online: " + str(mem_avg_online))
        logger.debug("mem_free_time: " + str(mem_free_time))
    if 'cpu_load_balance' in conf['metrics']:
        logger.debug("cpu_load_balance: " + str(cpu_load_balance))
    if 'mem_load_balance' in conf['metrics']:
        logger.debug("mem_load_balance: " + str(mem_load_balance))
    if 'io_avg_time' in conf['metrics']:
        logger.debug("io_avg_time: " + str(io_avg_time))
    if 'disk_usage' in conf['metrics']:
        logger.debug("disk_usage: " + str(disk_usage))
        disk_usage = temp_disk_usage / temp_disk_usage_cnt * 0.01
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
    if len(sys.argv) == 2:
        t = {}
        with open("./metrics/offline_times", 'r', encoding='utf-8') as f:
            t['offline'] = json.loads(f.read().replace("'", "\""))
        with open("./metrics/online_times", 'r', encoding='utf-8') as f:
            t['online'] = json.loads(f.read().replace("'", "\""))
        start = -1
        finish = -1
        for item in t['offline']:
            if start == -1 or (start != -1 and item['start'] < start):
                start = item['start']
            if finish == -1 or (finish != -1 and item['finish'] > finish):
                finish = item['finish']
        for item in t['online']:
            if start == -1 or (start != -1 and item['start'] < start):
                start = item['start']
            if finish == -1 or (finish != -1 and item['finish'] > finish):
                finish = item['finish']
        if sys.argv[1] == '-1':
            logger.warning("Cluster ID not specified. Use current metrics directly.")
        else:
            cluster_id = sys.argv[1]
            with open("./metrics/metrics", 'w', encoding='utf-8') as f:
                print(get_metrics(cluster_id, start, finish), file=f)
        with open("./metrics/metrics", 'r', encoding='utf-8') as f:
            m = json.loads(f.read().replace("'", "\""))
        score = analyze(m, t)

        ce = boto3.client('ce')
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': time.strftime("%Y-%m-%d", time.localtime(start)),
                'End': time.strftime("%Y-%m-%d", time.localtime(finish + 86400))
            },
            Granularity='DAILY',
            Metrics=[
                'UNBLENDED_COST',
            ]
        )
        costs = []
        for entry in response['ResultsByTime']:
            record = entry['Total']['UnblendedCost']
            shown = False
            for cost in costs:
                if cost['Unit'] == record['Unit']:
                    cost['Amount'] += record['Amount']
                    shown = True
                    break
            if not shown:
                costs.append(record)
        logger.info("--------------------------------")
        logger.info("Total cost:")
        for cost in costs:
            logger.info(str(cost['Amount']) + " " + str(cost['Unit']))
        logger.info("--------------------------------")
        logger.info("Benchmark finished.")
        logger.info("--------------------------------")
    else:
        logger.error("Invalid arguments. Please give cluster ID, start time and finish time.")
        logger.info("If you have collected metrics from CWAgent, please set cluster ID to -1.")
