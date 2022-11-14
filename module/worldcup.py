import pandas as pd
from collections import defaultdict
import csv

class GetTeams:
    def __init__(self, file_param):
        self.file = f"dependencies\{file_param}"

    def parse_data(self):
        columns = defaultdict(list)
        with open(self.file) as f:
            reader = csv.DictReader(f) # read rows into a dictionary format
            for row in reader: # read a row as {column1: value1, column2: value2,...}
                for (k,v) in row.items(): # go over each column name and value 
                    columns[k].append(v)
        print(columns['HomeTeam'])