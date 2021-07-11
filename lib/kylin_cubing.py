import time
import json
import requests
import sys
from Logger import Logger

logger = Logger('../log/benchmark.log', 'kylin_cubing')
cube_names = ["lineitem_cube", "partsupp_cube", "customer_vorder_cube", "customer_cube"]

for cube_name in cube_names:
    url = "http://localhost:7070/kylin/api/cubes/" + cube_name + "/rebuild"
    payload = "{\"buildType\":\"BUILD\",\"startTime\":757382400000,\"endTime\":915148800000," \
              "\"forceMergeEmptySegment\":false}"
    headers = {
        'Authorization': "Basic QURNSU46S1lMSU4=",
        'content-type': "application/json;charset=UTF-8"
    }
    response = requests.request("PUT", url, data=payload, headers=headers)
    uuid = json.loads(response.text)['uuid']
    logger.info("Build request sent, uuid is " + uuid)

    url = "http://localhost:7070/kylin/api/jobs"
    querystring = {"jobSearchMode":"ALL","limit":"15","offset":"0","projectName":"tpch","timeFilter":"2"}
    headers = {'Authorization': "Basic QURNSU46S1lMSU4="}

    message = {"uuid": uuid, "job_status": 'PENDING', "progress": 0}
    logger.info("Build is " + message['job_status'] + ". Progress is " + str(round(message['progress'], 1)))

    finished = False
    while finished is False:
        time.sleep(30)
        response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
        message = None
        for item in response:
            if item['uuid'] == uuid:
                message = item
                break
        if message is None:
            logger.error("uuid not found!")
            message = {'job_status': 'FINISHED'}
        else:
            logger.info("Build is " + message['job_status'] + ". Progress is " + str(round(message['progress'], 1)))
        finished = True
        if message['job_status'] != 'FINISHED':
            finished = False
