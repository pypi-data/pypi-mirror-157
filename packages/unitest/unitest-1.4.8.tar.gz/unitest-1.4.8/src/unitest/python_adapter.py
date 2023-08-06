import json
import os
import requests
import time

from decorator import decorator
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

registry = CollectorRegistry()
guage = Gauge("flow_probe_status", "Endpoint status", ["probeId", "probeName", "flowId", "flow_name"], registry=registry)

original_request_method = requests.request
PRETTY_OUTPUT = True

os.environ["ENABLE_REQUEST_ADAPTER"] = "False"
os.environ["SKIP_ADAPTER"] = "False"

header = {"Content-Type": "application/json"}


def trace():
    os.environ["SKIP_ADAPTER"] = "True"
    headers = dict()
    probe_url = f'https://proberunner.internal.mum1-stage.zetaapps.in/trace/headers'
    response = requests.get(url=probe_url, headers=header)
    os.environ["SKIP_ADAPTER"] = "False"
    try:
        headers = response.json()['traceHeaders']
    except:
        return headers
    return headers


@decorator
def adaptor(func, flow_id=None, *args, **kwargs):
    os.environ["FLOW_ID"] = flow_id
    return func(*args, **kwargs)


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
            header_dict: dict = kwargs.get('headers', None)
            if header_dict is not None:
                header_dict.update(trace())
            response = original_request_method(method, url, **kwargs)
            request = response.request
        finally:
            end_time = int(time.time() * 1000)

            adapter_data(start_time=start_time, end_time=end_time, request=request, response=response, method=method, url=url)
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


def adapter_data(*, start_time, end_time, request=None, response=None, method=None, url=None):
    if request is not None:
        trace_id = request.headers.get("X-Olympus-Traceid", None)
        flow_id = os.environ.get("FLOW_ID", None)

        if trace_id is not None and flow_id is not None:
            del os.environ["FLOW_ID"]

            if response.status_code >= 500:
                flag = 3
            else:
                flag = 1

            test_name = os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0]
            flow_probe_payload = test_name[test_name.find("[") + 1:test_name.find("]")]
            invocation_parameters = {
                "markers": test_name.replace("[" + flow_probe_payload + "]", "").replace("test_", "").replace("tests_", "").lower()
            }

            test_name = os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0]
            flow_probe_name = (test_name.split(":")[0].split(".")[0].replace("tests_", "").replace("test_", "").replace("_", " ").title())
            status_code = response.status_code
            trace_name = request.method
            duration = end_time - start_time

            create_probe_body = {
                "probeName": flow_probe_name,
                "description": "Testing on probe : '" + flow_probe_name.upper() + "' and flow ID : " + flow_id.upper(),
                "flowId": flow_id,
                "probeType": "FLOW",
                "probeRunnerType": "JENKINS",
                "crd": "test CRDx"
            }

            probe_data = [{
                "invocationURL": os.environ.get('url', None),
                "invocationParameters": invocation_parameters,
                "invocationStartTime": start_time,
                "invocationEndTime": end_time,
                "invocationDuration": duration,
                "traceId": trace_id,
                "traceName": trace_name,
                "statusCode": status_code,
                "status": flag
            }]

            probe_id = get_probe(flow_probe_name, flow_id)

            if probe_id != "":
                push_to_probe(probe_id, probe_data)
            else:
                probe_id = create_probe(create_probe_body)
                push_to_probe(probe_id, probe_data)

            flow_probe_name_with_id = f"{flow_probe_name}_{probe_id}"

            guage.labels(probe_id, flow_probe_name_with_id, flow_id, flow_id).set(flag)
            push_to_gateway("https://pushgateway.internal.mum1-stage.zetaapps.in/", job="PROBE-METRICS", registry=registry)


def get_probe(flow_probe_name, flow_id):
    os.environ["SKIP_ADAPTER"] = "True"
    url = f"https://proberunner.internal.mum1-stage.zetaapps.in/probe/{flow_probe_name}/flow/{flow_id}"
    response = requests.get(url, headers=header)
    os.environ["SKIP_ADAPTER"] = "False"
    if response.text:
        return response.json()["probeId"]
    else:
        return ""


def push_to_probe(probe_id, probe_data):
    os.environ["SKIP_ADAPTER"] = "True"
    url = f"https://proberunner.internal.mum1-stage.zetaapps.in/probe/{probe_id}/invocations"
    data = json.dumps(probe_data)
    response = requests.post(url, data=data, headers=header)
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
    response = requests.post(url, data=data, headers=header)
    os.environ["SKIP_ADAPTER"] = "False"
    if response.status_code == 200:
        return response.json()["probeId"]
    else:
        raise TypeError("Could not create a probe.")


def patcher():
    requests.api.request = logged_request
    requests.request = logged_request
