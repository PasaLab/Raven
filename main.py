import yaml
from testplans.testplan import Testplan
from lib.Logger import Logger
from lib.popen import subprocess_popen

def run():
    # initialize logger
    logger = Logger('./log/benchmark.log')

    # 0. Read yaml and check validity
    global_conf_file = open("config/config.yaml", encoding="UTF-8")
    global_conf = yaml.load(global_conf_file, Loader=yaml.FullLoader)

    try:
        if global_conf['engine'] not in ['spark-sql', 'custom']:
            logger.error("Failed: invalid engine type")
            return
        if global_conf['workload'] not in ['tpc-h', 'custom']:
            logger.error("Failed: invalid workload type")
            return
        if global_conf['test_plan'] not in ['one-pass', 'custom']:
            logger.error("Failed: invalid test plan type")
            return
        if global_conf['metrics'] not in ['time-based', 'custom']:
            logger.error("Failed: invalid metrics type")
            return
    except KeyError:
        logger.error("Failed: incomplete key-value pairs")
        return

    # 1. Launch the engine
    logger.info("Launching the engine...")
    if global_conf['engine'] == 'spark-sql':
        conf_file = open("config/engines/spark-sql.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from engines.sparksql import sparksql
        engine = sparksql()
        engine.set_app_name(conf['name'])
        try:
            engine.set_conf(conf['config'])
        except KeyError:
            engine.set_conf({})
        engine.launch()
    else:
        from engines.engine import engine
        engine = engine()
    logger.info("Engine launched successful!")
    logger.info("--------------------------------")

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
    logger.info("Generating workload successful!")
    logger.info("--------------------------------")

    # 3. Generate the execution plan
    logger.info("Generating execution plan...")
    plan = Testplan()
    if global_conf['test_plan'] == 'one-pass':
        conf_file = open("config/testplans/one-pass.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        from testplans.onepass import One_pass_testplan
        plan = One_pass_testplan()
        plan.build(conf)
    else:
        pass
    logger.info("Generating execution plan successful!")
    logger.info("--------------------------------")

    # 4. Execution and metrics acquisition
    logger.info("Executing queries...")
    plan.start(engine, workload.get_query())
    logger.info("Executing finished! Acquiring metrics...")
    logger.info("--------------------------------")

    # 5. Overhead calculation
    logger.info("Calculating overhead...")
    offline_metrics, online_metrics = plan.get_metrics()
    if global_conf['metrics'] == 'time-based':
        conf_file = open("config/metrics/time-based.yaml", encoding="UTF-8")
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        offline_time = 0
        online_time = 0
        for offline_metric in offline_metrics:
            for query in offline_metric:
                offline_time += query['time']
        for online_metric in online_metrics:
            for query in online_metric:
                online_time += query['time']
        time = offline_time
        offline_calculation_overhead = eval(str(conf['offline']['calculation']['eval']))
        offline_delay_overhead = eval(str(conf['offline']['delay']['eval']))
        time = online_time
        online_calculation_overhead = eval(str(conf['online']['calculation']['eval']))
        online_delay_overhead = eval(str(conf['online']['delay']['eval']))
        logger.info("Offline calculation: " + str(offline_calculation_overhead))
        logger.info("Offline delay: " + str(offline_delay_overhead))
        logger.info("Offline total: " + str(offline_calculation_overhead + offline_delay_overhead))
        logger.info("Online calculation: " + str(online_calculation_overhead))
        logger.info("Online delay: " + str(online_delay_overhead))
        logger.info("Online total: " + str(online_calculation_overhead + online_delay_overhead))
        offline = offline_calculation_overhead + offline_delay_overhead
        online = online_calculation_overhead + online_delay_overhead
        total = eval(str(conf['total']['eval']))
        logger.info("Total overhead: " + str(total))
    logger.info("Benchmark finished.")
    logger.info("--------------------------------")

if __name__ == '__main__':
    run()
    # run_on_aws()
