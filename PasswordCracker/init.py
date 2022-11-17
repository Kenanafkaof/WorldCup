from queue import Queue
import threading
from threading import Thread
import multiprocessing
from multiprocessing import Process, Manager, Value
import time 
import json
from passwordcracker import Cracker
from dependencies import passwords_raw, passwords_hashed
from logger import Logger

class Runtime:
    def __init__(self, password_param):
        self.start_time = time.time()
        self.retrieved_password = False
        self.index = password_param
        self.task_id = password_param + 1
        self.thread_queue = Queue()

    def init(self, queue):
        password_cracker = Cracker(passwords_raw, passwords_hashed, self.index, self.task_id)
        password_cracker.get_index()
        file = password_cracker.get_cracker_list()
        response = password_cracker.start_cracking(file)
        if response is not None:
            if response is False:
                execution_time = time.time() - self.start_time
                Logger(self.task_id, f"Could not find password. Starting brute force...").error()
                brute_force = password_cracker.brute_force()
                if brute_force is not None and brute_force is not False: 
                    self.retrieved_password = True
                elif brute_force is False:
                    Logger(self.task_id, f"Could not retrieve password in: {execution_time} seconds").error()
                Runtime.dump_data(self, response)
                queue.set(True)
                queue.get()
                queue.task_done()
                return self.retrieved_password
            else:
                self.retrieved_password = True
                execution_time = time.time() - self.start_time
                Logger(self.task_id, f"Total time elapsed: {execution_time} seconds").info()
                Runtime.dump_data(self, response)
                queue.get()
                queue.task_done()
                return self.retrieved_password

    def dump_data(self, password):
        response_data = []
        execution_time = time.time() - self.start_time
        with open("./dependencies/data.json", mode='a', encoding='utf-8') as feedsjson:
            entry = {'password': password.strip(), 'time': execution_time}
            response_data.append(entry)
            json.dump(response_data, feedsjson)
    
    def log(self, queue):
        iterations = 1
        while queue.get() is False:
            execution_time = time.time() - self.start_time
            Logger(self.task_id, f"Iteration count: {iterations}").info_cracker(execution_time)
            iterations += 1
        Logger(self.task_id, f"Disposing of thread: {self.task_id}").info()
        queue.get()
        queue.task_done()
        Logger(self.task_id, f"Successfully disposed of thread: {self.task_id}").success()

    def start(self, queue_initial):
        queue = multiprocessing.Queue()
        queue.put(self.retrieved_password)
        p = multiprocessing.Process(target=Runtime.log, args=(self, queue))
        p1 = multiprocessing.Process(target=Runtime.init, args=(self, queue))
        p.start()
        p1.start()
        p.join()
        p1.join()
        queue_initial.get()
        queue_initial.task_done()

    def thread(self, queue_initial):
        t = Thread(target=Runtime.init, args=(self, self.thread_queue))
        t1 = Thread(target=Runtime.log, args=(self, self.thread_queue))
        t.daemon = True
        t1.daemon = True
        t.start()
        t1.start()
        self.thread_queue.put(t)
        self.thread_queue.put(t1)
        self.thread_queue.join()
        queue_initial.get()
        queue_initial.task_done()