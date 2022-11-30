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

class Runtime:
    def __init__(self, password_hash, index, task_id, threads):
        self.start_time = time.time()
        self.threads = threads
        self.retrieved_password = False
        self.password = password_hash
        self.task_id = task_id
        self.index = index
        self.thread_queue = Queue()

    def brute(self, queue):
        password_cracker = Cracker(passwords_raw, self.password, self.index, self.task_id)
        returned_password = password_cracker.new_brute_force(self.password)
        if returned_password is not None:
            Logger(self.task_id, f"Successfully cracked password! Password is: {returned_password}").success()
            self.retrieved_password = True
            execution_time = time.time() - self.start_time
            Logger(self.task_id, f"Total time elapsed: {round(execution_time, 3)} seconds").info()
            queue.get()
            queue.task_done()
            Runtime.dump_data(self, returned_password)
            return self.retrieved_password

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
        time.sleep(1.5)
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

    def thread(self, queue_initial):
        threads = []

        for i in range(self.threads):
            t = Thread(target=Runtime.brute, args=(self, self.thread_queue))
            t.daemon = True
            t.start()
            threads.append(t)
        t1 = Thread(target=Runtime.log, args=(self, self.thread_queue))
        t1.daemon = True
        t1.start()
        
        #for task, log in zip(threads, threads_logging):
        for task in threads:
            self.thread_queue.put(task)
            self.thread_queue.put(t1)
            self.thread_queue.join()
            self.thread_queue.put(False)
            queue_initial.get()
            queue_initial.task_done()