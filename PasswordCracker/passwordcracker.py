from markupsafe import string
from logger import Logger
from threading import Thread
import hashlib, itertools
from tqdm import tqdm
import string
class Cracker:
    def __init__(self, password_result, password_hash, index, task_id):
        self.response = password_result
        self.password = password_hash
        self.index = index
        self.answer = self.response[self.index]
        self.id = task_id
        self.characters_all = list(string.ascii_letters) + list(string.digits) + list(string.punctuation)

    def return_password(self):
        return self.password

    #def get_cracker_list(self):
    #    file = open("./dependencies/realhuman_phill.txt","r", encoding = "ISO-8859-1")
    #    return file

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

    def new_brute_force(self, hash):
        self.password = hash
        for i in range(1, 9):
            total = int(len(self.characters_all)**i)
            for next_string in tqdm(itertools.product(self.characters_all, repeat=i),
                                    desc='progress',
                                    total=total,
                                    leave=False,
                                    unit=' strings',
                                    unit_scale=True):
                    test_string = str('').join(next_string)
                    hashed_string = hashlib.md5(test_string.encode())
                    test_hash = hashed_string.hexdigest()
                    if test_hash == self.password:
                        found_string = str(test_string)
                        return found_string
                    else:
                        pass
