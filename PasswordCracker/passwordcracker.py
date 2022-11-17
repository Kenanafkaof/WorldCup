from markupsafe import string
from logger import Logger
from threading import Thread
import hashlib, itertools

class Cracker:
    def __init__(self, password_result, password_hash, index_param, task_id):
        self.response = password_result
        self.password = password_hash
        self.index = index_param
        self.answer = self.response[self.index]
        self.id = task_id

    def get_index(self):
        self.password = self.password[self.index]
        return self.password

    def get_cracker_list(self):
        file = open("./dependencies/realhuman_phill.txt","r", encoding = "ISO-8859-1")
        return file

    def start_cracking(self, file):
        Logger(self.id, f"Starting password cracking for: {self.password}").info()
        for line in file:
            line = line.encode('utf-8')
            guess = hashlib.md5(line.strip()).hexdigest()
            if guess == self.password:
                solution = line.decode("utf-8")
                Logger(self.id, f"Retrieved password: {solution.strip()}").success()
                return solution
        return False

    
    def brute_force(self):
        for xs in itertools.product(string.ascii_letters, repeat=len(self.password)):
            s = ''.join(xs)
            if hashlib.md5(s.encode('utf-8')).hexdigest() == self.password:
                Logger(self.id, f"Retrieved password: {s.strip()}").success()
                return s


