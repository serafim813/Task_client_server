import socket
from threading import Thread
from queue import Queue

from protocol import TaskIdRes, DataRes, StatusRes, deserialize
import protocol as prt
from tasks import TaskStorage, Task


class Server:
    def __init__(self, host, port, timeout: int = None):
        self.host = host
        self.port = port
        self.connection_limit = 1000
        self.receiving_buffer_size = 1024
        self.tasks = TaskStorage()
        self.input_tasks = Queue()
        self.workers = {}
        self.timeout = timeout
        self.stop = False

    def set_worker(self, task_type: str, worker):
        self.workers[task_type] = worker

    def run(self):
        # start worker thread
        worker_thread = Thread(target=self._worker_loop)
        worker_thread.start()
        # init socket
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind((self.host, self.port))
        listener.listen()
        clients_threads = []
        clients_sockets = []
        # wait connections
        while True:
            try:
                client_socket, addr = listener.accept()  # if more then lim?
                thread = Thread(target=self._connection, args=(client_socket,))
                thread.start()
                clients_threads.append(thread)
                clients_sockets.append(client_socket)
            except KeyboardInterrupt:
                listener.close()
                self.stop = True
                self.input_tasks.put(None)
                worker_thread.join()
                [task[1].close() for task in list(self.input_tasks.queue) if task is not None]
                for client_socket in clients_sockets:
                    client_socket.close()
                for client_thread in clients_threads:
                    client_thread.join()
                break

    def _worker_loop(self):
        while not self.stop:
            next_task = self.input_tasks.get()
            if next_task is None:
                continue
            task_id, sender_socket = next_task
            task = self.tasks.get(task_id)
            try:
                task.on_execution()
                result = self.workers[task.task_type](task.data)
                task.set_result(result)
            except Exception as e:
                print(e)
                task.set_error_message(str(e))

            try:
                sender_socket.sendall(task.status.encode("utf-8"))
            except socket.error:
                pass

    def _connection(self, client_socket):
        client_socket.settimeout(self.timeout)
        try:
            request = deserialize(client_socket.recv(self.receiving_buffer_size))
        except Exception:
            client_socket.close()
            exit()
        if request.get(prt.TYPE) == prt.RUN:
            # run new task
            task = Task(request.get(prt.TASK_NAME), request.get(prt.DATA))
            task_id = self.tasks.put(task)
            try:
                client_socket.sendall(TaskIdRes(task_id).serialize())
            except socket.error:
                client_socket.close()
                return
            worker_socket, waiter_socket = socket.socketpair()
            self.input_tasks.put((task_id, waiter_socket))
            status = worker_socket.recv(self.receiving_buffer_size)
            try:
                status_request = deserialize(client_socket.recv(self.receiving_buffer_size))
            except Exception:
                status_request = None
            if status_request:
                if status_request.get(prt.TYPE) == prt.STATUS and status_request.get(prt.TASK_ID) == task_id:
                    try:
                        client_socket.sendall(StatusRes(task.status).serialize())
                    except socket.error:
                        pass
            client_socket.close()
            worker_socket.close()
            waiter_socket.close()
        elif request.get(prt.TYPE) == prt.STATUS:
            # return task status
            task = self.tasks.get(request.get(prt.TASK_ID))
            if task:
                try: 
                    client_socket.sendall(StatusRes(task.status).serialize())
                except socket.error as e:
                    pass
            client_socket.close()
        elif request.get(prt.TYPE) == prt.GET_RESULT:
            # return task result and status
            task = self.tasks.get(request.get(prt.TASK_ID))
            if task:
                data, status = task.get_result()
                try:
                    client_socket.sendall(DataRes(data, status).serialize())
                except socket.error:
                    pass
            client_socket.close()
        else:
            client_socket.close()

            
