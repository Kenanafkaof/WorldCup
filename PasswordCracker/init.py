import threading
from threading import Thread
import multiprocessing
from queue import Queue
from multiprocessing import Process, Manager, Value
import time 
import json
from passwordcracker import Cracker
from dependencies import passwords_raw, passwords_hashed
from logger import Logger
from md5_init import md5

def brute_force(queue, password, index, task_id, start_time):
    password_cracker = Cracker(passwords_raw, password, index, task_id)
    print("running...")
    returned_password = password_cracker.new_brute_force(password)
    if returned_password is not None:
        Logger(task_id, f"Successfully cracked password! Password is: {returned_password}").success()
        retrieved_password = True
        execution_time = time.time() - start_time
        Logger(task_id, f"Total time elapsed: {execution_time} seconds").info()
        queue.get()
        queue.task_done()
        return retrieved_password

class Runtime:
    def __init__(self, password_hash, index, task_id, threads):
        self.start_time = time.time()
        self.threads = threads
        self.retrieved_password = False
        self.password = password_hash
        self.task_id = task_id
        self.index = index
        self.thread_queue = Queue()

    def brute_force(self):
        function_init = md5(self.password, self.index, self.task_id, self.start_time).brute_force()

    def thread_password(self, queue):
        threads = []
        function_init = md5(self.password, self.index, self.task_id, self.start_time)

        for i in range(self.threads):
            p = Thread(target=function_init.brute_force, args=(self, queue))
            p.start()
            threads.append(p)

        for p in threads:
            p.join()
        self.thread_queue.join()
        self.thread_queue.get()
        self.thread_queue.task_done()

    def init(self, queue):
        password_cracker = Cracker(passwords_raw, passwords_hashed, self.index, self.task_id)
        password_cracker.get_index()
        file = password_cracker.get_cracker_list()
        response = password_cracker.start_cracking(file)
        if response is not None:
            if response is False:
                execution_time = time.time() - self.start_time
                Logger(self.task_id, f"Could not find password. Starting brute force...").error()
                brute_force = password_cracker.new_brute_force()
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
        time.sleep(3)
        while self.retrieved_password is False:
            execution_time = time.time() - self.start_time
            Logger(self.task_id, f"Iteration count: {iterations}").info_cracker(execution_time)
            iterations += 1
        print("===========================================================================================================")
        Logger(self.task_id, f"Disposing of thread: {self.task_id}").info()
        queue.get()
        queue.task_done()
        Logger(self.task_id, f"Successfully disposed of thread: {self.task_id}").success()
        print("===========================================================================================================")

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
        for i in range(self.threads):
            t = Thread(target=Runtime.brute_force, args=(self))
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