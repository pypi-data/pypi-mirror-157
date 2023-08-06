import json
import os
import requests
import time

# sys.path.append(os.path.dirname(__file__))
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

registry = CollectorRegistry()
guage = Gauge(
    "flow_probe_status",
    "Endpoint status",
    ["probeId", "probeName", "flowId", "flow_name"],
    registry=registry,
)


original_request_method = requests.request
PRETTY_OUTPUT = True


os.environ["ENABLE_REQUEST_ADAPTER"] = "False"
os.environ["SKIP_ADAPTER"] = "False"

def logged_request(method, url, **kwargs):
    if os.environ["SKIP_ADAPTER"] == "False":
        os.environ["ENABLE_REQUEST_ADAPTER"] = "False"
        test_name = os.environ.get("PYTEST_CURRENT_TEST")

        if "call" in test_name:
            os.environ["ENABLE_REQUEST_ADAPTER"] = "True"
        enabled = os.environ.get("ENABLE_REQUEST_ADAPTER").lower()[0] in ("y", "t")
        if not enabled:
            return original_request_method(method, url, **kwargs)

        request = None
        response = None
        start_time = int(time.time() * 1000)

        try:
            response = original_request_method(method, url, **kwargs)
            request = response.request
        finally:
            end_time = int(time.time() * 1000)

            adapter_data(
                start_time=start_time,
                end_time=end_time,
                request=request,
                response=response,
                method=method,
                url=url,
            )
        return response
    else:
        return original_request_method(method, url, **kwargs)



def is_protected(key):
    key_lower = key.lower()
    for test in ("auth", "secret"):
        if test in key_lower:
            return True
    return False


def sanitize_data(data: dict):
    return {k: "******" if is_protected(k) else v for k, v in data.items()}

 
 

def adapter_data(
    *, start_time, end_time, request=None, response=None, method=None, url=None
):

    if response.status_code >= 500:
        flag = 3
    else:
        flag = 1

    test_name = os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0]
    flow_probe_payload = test_name[test_name.find("[")+1:test_name.find("]")]
    invocation_parmaters = {
                    "markers":
                            test_name.replace("["+flow_probe_payload+"]","").replace("test_","").replace("tests_","").lower()
                            }

    test_name = os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0]
    flow_probe_name = (
        test_name.split(":")[0]
        .split(".")[0]
        .replace("tests_", "")
        .replace("test_", "")
        .replace("_", " ")
        .title()
    )
    flow_id = os.environ.get("FLOW_ID")
    status_code = response.status_code
    trace_id = request.headers.get("X-Olympus-Traceid", None)
    trace_name = request.method
    duration = end_time - start_time

    
    
    create_probe_body={
            "probeName": flow_probe_name,
            "description": "Testing on probe : '"+flow_probe_name.upper()+"' and flow ID : "+flow_id.upper(),
            "flowId": flow_id,
            "probeType": "FLOW",
            "probeRunnerType": "JENKINS",
            "crd": "test CRDx"
                    }
    probe_data=[{
        "invocationURL": os.environ.get('url',None),
        "invocationParameters":invocation_parmaters,
        "invocationStartTime":start_time,
        "invocationEndTime":end_time,
        "invocationDuration":duration,
        "traceId": trace_id,
        "traceName": trace_name,
        "statusCode": status_code,
        "status": flag
                }]
    
      
    # write_json(probe_data, create_probe_body)


    probe_id = get_probe(flow_probe_name, flow_id)

    if probe_id != "":
        push_to_probe(probe_id, probe_data)
    else:
        probe_id = create_probe(create_probe_body)
        push_to_probe(probe_id, probe_data)

    flow_probe_name_with_id = f"{flow_probe_name}_{probe_id}"

    guage.labels(probe_id, flow_probe_name_with_id, flow_id, flow_id).set(flag)
    push_to_gateway(
        "https://pushgateway.internal.mum1-stage.zetaapps.in/",
        job="PROBE-METRICS",
        registry=registry,
    )


                    
 
 
def get_probe(flow_probe_name, flow_id):
    os.environ["SKIP_ADAPTER"] = "True"
    url = f"https://proberunner.internal.mum1-stage.zetaapps.in/probe/{flow_probe_name}/flow/{flow_id}"
    response = requests.get(url, headers={"Content-Type": "application/json"})
    os.environ["SKIP_ADAPTER"] = "False"
    if response.text:
        return response.json()["probeId"]
    else:
        return ""


def push_to_probe(probe_id, probe_data):
    os.environ["SKIP_ADAPTER"] = "True"
    url = f"https://proberunner.internal.mum1-stage.zetaapps.in/probe/{probe_id}/invocations"
    data = json.dumps(probe_data)
    response = requests.post(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    if response.status_code != 200:
        return response.text
    os.environ["SKIP_ADAPTER"] = "False"
    if response.text == "1 invocations saved":
        return True
    else:
        if response.json()["message"] == "failure to get a peer from the ring-balancer":
            return True


def create_probe(create_probe_body):
    os.environ["SKIP_ADAPTER"] = "True"
    url = "https://proberunner.internal.mum1-stage.zetaapps.in/probe"
    data = json.dumps(create_probe_body)
    response = requests.post(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    os.environ["SKIP_ADAPTER"] = "False"
    if response.status_code == 200:
        return response.json()["probeId"]
    else:
        raise TypeError("couldnt create a probe")


def write_json(data, data1, field="adapter_data", file_name="data1.json"):
    with open(file_name, "r ") as file:
        file_data = json.load(file)
        s = [data, data1]
        file_data[field].append(s)
        file.seek(0)
        json.dump(file_data, file, indent=6)



def patcher():
    requests.api.request = logged_request
    requests.request = logged_request

    

