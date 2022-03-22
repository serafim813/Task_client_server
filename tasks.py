from threading import Lock

WAITING = 'waiting'
SUCCESS = 'success'
ERROR = 'error'
EXECUTE = 'execute'

class Task:
    def __init__(self, task_type, data):
        self.__task_type = task_type
        self.__data = data
        self.__status = WAITING
        self.__result = None
        self.__error_message = ""
        self.lock = Lock()

    @property
    def task_type(self):
        return self.__task_type

    @property
    def data(self):
        return self.__data

    @property
    def status(self):
        with self.lock:
            return self.__status

    def on_execution(self):
        with self.lock:
            self.__status = EXECUTE

    def set_result(self, result):
        with self.lock:
            self.__status = SUCCESS
            self.__result = result

    def get_result(self):
        with self.lock:
            status = self.__status
            result = self.__result
        return result, status

    def set_error_message(self, message: str):
        with self.lock:
            self.__status = ERROR
            self.__error_message = message

    def get_error_message(self):
        with self.lock:
            status = self.__status
            error = self.__error_message
        return error, status


class TaskStorage:
    def __init__(self):
        self.__task_list = []
        self.__lock = Lock()

    def put(self, task: Task) -> int:
        with self.__lock:
            self.__task_list.append(task)
            task_id = len(self.__task_list) - 1
        return task_id

    def get(self, task_id: int) -> Task or None:
        if type(task_id) is not int:
            return None
        with self.__lock:
            task = None
            if 0 <= task_id < len(self.__task_list):
                task = self.__task_list[task_id]
        return task

