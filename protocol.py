import json

TYPE = 'type'
STATUS = 'status'
RUN = 'run'
GET_RESULT = 'get_result'

TASK_NAME = 'task_name'
DATA = 'data'
TASK_ID = 'task_id'


class Protocol:
    def serialize(self):
        return json.dumps(self.request).encode("utf-8")


class TaskReq(Protocol):
    def __init__(self, task_name: str, data):
        self.request = {TYPE: RUN,
                        TASK_NAME: task_name,
                        DATA: data}


class StatusReq(Protocol):
    def __init__(self, task_id: int):
        self.request = {TYPE: STATUS,
                        TASK_ID: task_id}


class ResultReq(Protocol):
    def __init__(self, task_id: int):
        self.request = {TYPE: GET_RESULT,
                        TASK_ID: task_id}


class TaskIdRes(Protocol):
    def __init__(self, task_id: int):
        self.request = {TASK_ID: task_id}


class DataRes(Protocol):
    def __init__(self, data, status):
        self.request = {STATUS: status,
                        DATA: data}


class StatusRes(Protocol):
    def __init__(self, status):
        self.request = {STATUS: status}


def deserialize(data):
    try:
        return json.loads(data)
    except json.decoder.JSONDecodeError:
        return {}
