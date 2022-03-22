#!/bin/python
from time import sleep

import worker
from server import Server


def execution_delay(function, delay=0):
    '''Sets the execution delay of the function to simulate the execution time'''
    def wrapper(data):
        sleep(delay)
        return function(data)
    return wrapper


if __name__ == "__main__":
    test_server = Server(host="localhost",
                         port=4321,
                         timeout=100)

    # set workers
    test_server.set_worker(task_type="1", worker=execution_delay(worker.revers, 2))
    test_server.set_worker(task_type="2", worker=execution_delay(worker.permutation, 5))
    test_server.set_worker(task_type="3", worker=execution_delay(worker.repeat, 7))

    # run server
    test_server.run()

    
