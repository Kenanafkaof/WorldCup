import string

charset_full = list(string.ascii_letters) + list(string.digits) + list(string.punctuation)

print(charset_full)

#def start(self, queue_initial):
#    queue = multiprocessing.Queue()
 #   queue.put(self.retrieved_password)
 #   p = multiprocessing.Process(target=Runtime.log, args=(self, queue))
 #   p1 = multiprocessing.Process(target=Runtime.init, args=(self, queue))
 #   p.start()
  #  p1.start()
  #  p.join()
  #  p1.join()
  #  queue_initial.get()
  #  queue_initial.task_done()

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

    #def get_cracker_list(self):
    #    file = open("./dependencies/realhuman_phill.txt","r", encoding = "ISO-8859-1")
    #    return file