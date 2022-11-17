from datetime import datetime
import psutil
import time 
from time import sleep


class Colors(object):
    def __init__(self):
        self.MAIN = '\033[37m' #\033[90m
        self.HEADER = '\033[95m'
        self.INFO = '\033[94m'
        self.OKCYAN = '\033[96m'
        self.SUCCESS = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

class Logger(object):
    def __init__(self, task_id, message):
        self.id = task_id
        now = datetime.now()
        self.time = now.strftime("%m-%d-%Y %H:%M:%S")   
        self.message = message 

    def validate_response(self, response):
        if response == 200:
            return f"{Colors().SUCCESS}{response} OK{Colors().ENDC}"
        elif response == 302:
            return f"{Colors().WARNING}{response} REDIRECT{Colors().ENDC}"
        elif response == 403:
            return f"{Colors().WARNING}{response} BANNED{Colors().ENDC}"
        else:
            return f"{Colors().FAIL}{response} ERROR{Colors().ENDC}"

    def return_wrapper(self):
        return f"[{Colors().MAIN}{self.time}{Colors().ENDC}] [{Colors().MAIN}TaskID: {self.id}{Colors().ENDC}] "
    
    def error(self):
        print(Logger.return_wrapper(self) + f"[{Colors().MAIN}Type: {Colors().FAIL}ERROR{Colors().ENDC}] {self.message} {Colors().ENDC}")

    def success(self):
        print(Logger.return_wrapper(self) + f"[{Colors().MAIN}Type: {Colors().SUCCESS}SUCCESS{Colors().ENDC}] {self.message} {Colors().ENDC}")

    def warn(self):
        print(Logger.return_wrapper(self) + f"[{Colors().MAIN}Type: {Colors().WARNING}WARN{Colors().ENDC}] {self.message} {Colors().ENDC}")

    def info(self):
        print(Logger.return_wrapper(self) + f"[{Colors().MAIN}Type: {Colors().INFO}INFO{Colors().ENDC}] {self.message} {Colors().ENDC}")

    def get_hardware(self):        
        return f"[{Colors().MAIN}CPU: {psutil.cpu_percent(4)}%{Colors().ENDC}] [{Colors().MAIN}RAM Memory: {psutil.virtual_memory()[2]}%{Colors().ENDC}] [{Colors().MAIN}RAM GB: {psutil.virtual_memory()[3]/1000000000} GB{Colors().MAIN}]{Colors().ENDC}"
    
    def info_cracker(self, execution_time):   
        print(Logger.return_wrapper(self) + f"[{Colors().MAIN}Type: {Colors().WARNING}WORKING{Colors().ENDC}] [{Colors().MAIN}Time Elapsed: {round(execution_time, 3)} seconds{Colors().ENDC}] " + Logger.get_hardware(self) + f": {self.message}")
        time.sleep(5)