import requests
import os

def trace():
    os.environ["SKIP_ADAPTER"] = "False"
    headers=dict()
    probe_url=f'https://proberunner.internal.mum1-stage.zetaapps.in/trace/headers'
    response=requests.get(url=probe_url,headers={"Content-Type": "application/json"})
    os.environ["SKIP_ADAPTER"] = "False"
    try:
        headers=response.json()['traceHeaders']
        print(headers)
    except:
        return headers
    return headers


# import time
# import hmac
# from base64 import b64encode
# from hashlib import md5
# import uuid





# def trace():

#     headers = {}
#     client_id = "probes_service"
#     secret = b"70b5d519ad5c40d7a344563dec9e7b5c"
#     trace_id = uuid.uuid4().hex
#     timestamp = str(int(time.time()) // 60)
#     headers["X-Olympus-Timestamp"] = timestamp
#     headers["X-Olympus-Traceid"] = trace_id
#     headers["X-Olympus-Client-Id"] = client_id
#     trace_token = hmac.new(
#         secret,
#         "{0}-{1}-{2}".format(client_id, str(trace_id), str(timestamp)).encode("utf-8"),
#         digestmod=md5,
#     ).hexdigest()
#     # print(len(trace_token))
#     headers["X-Olympus-Trace-Token"] = trace_token
#     return headers