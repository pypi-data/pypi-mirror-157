import os
from decorator import decorator
from Config.trace_id import trace
import os
import sys

sys.path.append(os.path.dirname(__file__))


@decorator
def adaptor(func, flow_id=None, *args, **kwargs):
    os.environ["FLOW_ID"] = flow_id
    if args:
        for i in args:
            if isinstance(i, dict):
                i.update(trace())
    return func(*args, **kwargs)


  
