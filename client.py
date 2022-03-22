import socket
from sys import exit
from protocol import TaskReq, StatusReq, ResultReq, deserialize
import protocol as p


class Client:
    def __init__(self, host, port, receiving_buffer_size):
        self.host = host
        self.port = port
        self.receiving_buffer_size = receiving_buffer_size

    def run(self, task_name: str, data: str) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            request = TaskReq(task_name, data).serialize()
            sock.sendall(request)
            response = deserialize(sock.recv(self.receiving_buffer_size))
        return response.get(p.TASK_ID)

    def run_and_wait_status(self, task_name: str, data: str) -> (int, str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(TaskReq(task_name, data).serialize())
            response = deserialize(sock.recv(self.receiving_buffer_size))
            task_id = response.get(p.TASK_ID)
            sock.sendall(StatusReq(task_id).serialize())
            response = deserialize(sock.recv(self.receiving_buffer_size))
            status = response.get(p.STATUS)
        return task_id, status

    def task_status(self, task_id: int) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(StatusReq(task_id).serialize())
            response = deserialize(sock.recv(self.receiving_buffer_size))
            status = response.get(p.STATUS)
        return status

    def task_result(self, task_id: int) -> (str, str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(ResultReq(task_id).serialize())
            response = deserialize(sock.recv(self.receiving_buffer_size))
            status = response.get(p.STATUS)
            data = response.get(p.DATA)
        return data, status


if __name__ == '__main__':
    from argparse import ArgumentParser

    argp = ArgumentParser()
    argp.add_argument("--action", "-a", type=str, action="store", dest="action", required=True)
    argp.add_argument("--data", "-d", type=str, action="store", dest="data", default="", required=False)
    argp.add_argument("--task_name", "-n", type=str, action="store", dest="task_name", default="", required=False)
    argp.add_argument("--waiting_for_data", "-w", type=bool, action="store", dest="waiting_for_data", default=False,
                      required=False)
    args = argp.parse_args()

    client = Client(host="localhost",
                    port=4321,
                    receiving_buffer_size=1024
                    )

    #  actions
    STATUS = "status"  # get task status
    RESULT = "result"  # get task result
    RUN = "run"  # run new task

    if args.action == STATUS:
        try:
            task_id = int(args.data)
        except ValueError:
            print(f"ERROR: incorrect value of data [{args.data}]. Integer type expected.")
            exit()
        status = client.task_status(task_id)
        if status is not None:
            print(f"Status of task #{task_id}: {status}")
        else:
            print(f"ERROR: failed to get task status. Task #{task_id}")
    elif args.action == RESULT:
        try:
            task_id = int(args.data)
        except ValueError:
            print(f"ERROR: incorrect value of data [{args.data}]. Integer type expected.")
            exit()
        result, status = client.task_result(int(task_id))
        if status is not None:
            print(f"Result of task #{task_id}: {result}")
            print(f"Status: {status}")
        else:
            print(f"ERROR: failed to get task result. Task #{args.data}")
    elif args.action == RUN:
        if args.waiting_for_data:
            task_id, status = client.run_and_wait_status(args.task_name, args.data)
            if status is not None:
                result, st = client.task_result(task_id)
                print(f"Result of task #{task_id} [{args.task_name}]: {result}")
                print(f"Status: {st}")
            else:
                print(f"ERROR: failed to complete the task {args.task_name}")
        else:
            task_id = client.run(args.task_name, args.data)
            if task_id is not None:
                print(f"Task [{args.task_name}] added to the queue. Task id is #{task_id}")
            else:
                print(f"ERROR: failed to start task {args.task_name}")
    else:
        print(f"ERROR: unknown action {args.action}")


