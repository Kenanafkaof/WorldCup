from passwordcracker import Cracker
from multiprocessing.dummy import Pool as ThreadPool
from dependencies import passwords_raw, passwords_hashed
from logger import Logger
import time 

class md5:
    def __init__(self, password, index, task_id, start_time):
        self.password = password
        self.index = index
        self.task_id = task_id
        self.start_time = start_time

    def brute_force(self, queue):
        password_cracker = Cracker(passwords_raw, self.password, self.index, self.task_id)
        print("running...")
        returned_password = password_cracker.new_brute_force(self.password)
        if returned_password is not None:
            Logger(self.task_id, f"Successfully cracked password! Password is: {returned_password}").success()
            retrieved_password = True
            execution_time = time.time() - self.start_time
            Logger(self.task_id, f"Total time elapsed: {execution_time} seconds").info()
            queue.get()
            queue.task_done()
            return retrieved_password
