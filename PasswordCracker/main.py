from init import Runtime
from dependencies import passwords_raw, passwords_hashed
from threading import Thread
from queue import Queue
from logger import Logger
import uuid

def main():
    index = 0 
    Logger("Password Cracker Notification", "Initializing password cracker...").info()
    task_id = str(uuid.uuid4())[:8]
    thread_queue = Queue()
    task = Runtime(passwords_hashed[index], index, task_id, threads=2)
    t = Thread(target=task.thread, args=(thread_queue,))
    t.daemon = True
    t.start()
    thread_queue.put(t)
    thread_queue.join()

if __name__ == "__main__":
    main()