import time
import json
import requests

url = "http://localhost:7070/kylin/api/cubes/TPCH_Q1/build"
payload = "{\"buildType\":\"BUILD\",\"startTime\":0,\"endTime\":0}"
headers = {
    'Authorization': "Basic QURNSU46S1lMSU4=",
    'content-type': "application/json;charset=UTF-8"
}
response = requests.request("PUT", url, data=payload, headers=headers)
uuid = json.loads(response.text)['uuid']
print(uuid)
url = "http://localhost:7070/kylin/api/jobs"
querystring = {"jobSearchMode":"ALL","limit":"15","offset":"0","projectName":"tpch","timeFilter":"2"}
headers = {'Authorization': "Basic QURNSU46S1lMSU4="}
message = {"uuid": uuid, "job_status": 'PENDING', "progress": 0}
print(message['job_status'], message['progress'])
while message['job_status'] != 'FAILED' or 'FINISHED':
    time.sleep(30)
    response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
    message = None
    for item in response:
        if item['uuid'] == uuid:
            message = item
            break
    if message is None:
        print("uuid not found!")
        message = {'job_status': 'FAILED'}
    else:
        print(message['job_status'], message['progress'])
