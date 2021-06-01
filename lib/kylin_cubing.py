import time
import json
import requests
import sys
from lib.Logger import Logger

logger = Logger('./log/benchmark.log', 'kylin_cubing')
cube_name = ""
if len(sys.argv) == 2:
    cube_name = sys.argv[1]
else:
    logger.error("Invalid argument. Please give a valid cube name to build")

url = "http://localhost:7070/kylin/api/cubes/" + cube_name + "/build"
payload = "{\"buildType\":\"BUILD\",\"startTime\":0,\"endTime\":0}"
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
while message['job_status'] != 'FINISHED':
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
