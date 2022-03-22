def revers(data):
    return data[::-1]


def permutation(data):
    odd = data[::2]
    even = data[1::2]
    result = ''
    for i in range(len(even)):
        result += even[i]
        result += odd[i]
    if len(odd) != len(even):
        result += odd[-1]
    return result


def repeat(data):
    task = []
    for i in range(len(data)):
        task.append((i + 1) * data[i])
    task_str = "".join(task)
    return task_str

