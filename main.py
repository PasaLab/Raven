import sys
import time
import yaml
from testplans.testplan import Testplan
from lib.boto3sdk import upload
from lib.Logger import Logger


def generate():
    # 1. Read yaml and check validity
    global_conf_file = open("config/config.yaml", encoding="UTF-8")
    global_conf = yaml.load(global_conf_file, Loader=yaml.FullLoader)

    try:
        if global_conf['engine'] not in ['spark-sql', 'kylin', 'custom']:
            logger.error("Failed: invalid engine type")
            return
        if global_conf['workload'] not in ['tpc-h', 'custom']:
            logger.error("Failed: invalid workload type")
            return
        if global_conf['test_plan'] not in ['one-pass', 'one-pass-concurrent', 'one-offline-multi-online', 'custom']:
            logger.error("Failed: invalid test plan type")
            return
    except KeyError:
        logger.error("Failed: incomplete key-value pairs")
        return

    # 2. Generate the workload
    logger.info("Generating workload...")
    if global_conf['workload'] == 'tpc-h':
        conf_file = open("config/workloads/tpch.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from workloads.tpch import tpch
        workload = tpch()
        workload.set_switch(conf['switch'])
        workload.set_conf(conf['config'])
        if conf['switch']['generate'] is True:
            workload.generate()
            logger.info("Generating data successful!")
        else:
            logger.info("Generating data skipped!")


def run():
    start = time.time()
    global_conf_file = open("config/config.yaml", encoding="UTF-8")
    global_conf = yaml.load(global_conf_file, Loader=yaml.FullLoader)
    # 3. Launch the engine
    logger.info("Launching the engine...")
    if global_conf['engine'] == 'spark-sql':
        conf_file = open("config/engines/spark-sql.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from engines.sparksql import sparksql
        engine = sparksql()
        engine.set_app_name(conf['name'])
    if global_conf['engine'] == 'kylin':
        conf_file = open("config/engines/kylin.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from engines.kylin import kylin
        engine = kylin()
    else:
        from engines.engine import engine
        engine = engine()
    try:
        engine.set_conf(conf['config'])
    except KeyError:
        engine.set_conf({})
    engine.launch()
    logger.info("Engine launched successful!")
    logger.info("--------------------------------")

    # 4. Generate warehouse
    logger.info("Generating warehouse...")
    if global_conf['workload'] == 'tpc-h':
        conf_file = open("config/workloads/tpch.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from workloads.tpch import tpch
        workload = tpch()
        workload.set_switch(conf['switch'])
        workload.set_conf(conf['config'])
        if conf['switch']['create'] is True:
            workload.create(engine)
            logger.info("Creating data tables successful!")
        else:
            logger.info("Creating data tables skipped!")
        if conf['switch']['load'] is True:
            workload.load(engine)
            logger.info("Loading data to warehouse successful!")
        else:
            logger.info("Loading data to warehouse skipped!")
        workload.set_query(conf['query'])
    else:
        from workloads.workload import workload
        workload = workload()
    logger.info("Workload generated!")
    logger.info("--------------------------------")

    # 5. Generate the execution plan
    logger.info("Generating execution plan...")
    plan = Testplan()
    if global_conf['test_plan'] == 'one-pass':
        conf_file = open("config/testplans/one-pass.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from testplans.onepass import One_pass_testplan
        plan = One_pass_testplan()
        plan.build(conf)
    if global_conf['test_plan'] == 'one-pass-concurrent':
        conf_file = open("config/testplans/one-pass-concurrent.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from testplans.onepassConcurrent import One_pass_concurrent_testplan
        plan = One_pass_concurrent_testplan()
        plan.build(conf)
    if global_conf['test_plan'] == 'one-offline-multi-online':
        conf_file = open("config/testplans/one-offline-multi-online.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from testplans.oneOfflineMultiOnline import One_offline_multi_online_testplan
        plan = One_offline_multi_online_testplan()
        plan.build(conf)
    else:
        pass
    logger.info("Generating execution plan successful!")
    logger.info("--------------------------------")

    # 6. Execution and metrics acquisition
    logger.info("Executing queries...")
    plan.start(engine, workload.get_query())
    logger.info("Execution finished!")

    offline_metrics, online_metrics = plan.get_metrics()
    offline_times = []
    online_times = []
    for offline_metric in offline_metrics:
        for query in offline_metric:
            offline_times.append(query)
    for online_metric in online_metrics:
        for query in online_metric:
            online_times.append(query)
    logger.info("Offline times...")
    logger.info(str(offline_times))
    logger.info("--------------------------------")
    logger.info("Online times...")
    logger.info(str(online_times))
    logger.info("--------------------------------")
    with open("./offline_times", 'w', encoding='utf-8') as f:
        print(str(offline_times), file=f)
    with open("./online_times", 'w', encoding='utf-8') as f:
        print(str(online_times), file=f)
    upload("./offline_times", "olapstorage", "tmp/offline_times")
    upload("./online_times", "olapstorage", "tmp/online_times")

    finish = time.time()
    logger.info("Job started at: " + str(start))
    logger.info("Job finished at: " + str(finish))
    logger.info("Please acquire other metrics on the monitor.")
    logger.info("--------------------------------")


if __name__ == '__main__':
    logger = Logger('./log/benchmark.log', 'main')
    if len(sys.argv) == 2:
        if sys.argv[1] == "generate":
            generate()
        elif sys.argv[1] == "run":
            run()
        else:
            logger.error("Invalid argument: " + sys.argv[1])
            logger.error("Usage: generate | run")
    else:
        logger.error("Invalid number of arguments!")
        logger.error("Usage: generate | run")
