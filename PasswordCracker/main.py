from init import Runtime
from dependencies import passwords_raw, passwords_hashed
import threading
from threading import Thread
from queue import Queue

def main():
    thread_queue = Queue()
    for password in range(len(passwords_hashed) - 5):
        task = Runtime(password)
        t = Thread(target=task.thread, args=(thread_queue,))
        t.daemon = True
        t.start()
        thread_queue.put(t)
    thread_queue.join()
    #for password in range(len(passwords_hashed) - 6):
    #    Runtime(password).thread()
   # Runtime(3).start()

if __name__ == "__main__":
    main()