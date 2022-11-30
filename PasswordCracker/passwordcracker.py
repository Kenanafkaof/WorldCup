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

    def new_brute_force(self, hash):
        self.password = hash
        for i in range(1, 9):
            total = int(len(self.characters_all)**i)
            for next_string in tqdm(itertools.product(self.characters_all, repeat=i),
                                    desc='progress',
                                    total=total,
                                    leave=False,
                                    unit=' strings',
                                    unit_scale=True, 
                                    disable=True):
                    test_string = str('').join(next_string)
                    hashed_string = hashlib.md5(test_string.encode())
                    test_hash = hashed_string.hexdigest()
                    if test_hash == self.password:
                        found_string = str(test_string)
                        return found_string
                    else:
                        pass
