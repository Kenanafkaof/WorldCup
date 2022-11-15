from itertools import count
from collections import defaultdict
import csv

class GetTeams:
    def __init__(self, file_param):
        self.file = f"dependencies/{file_param}"

    def parse_data(self):
        columns = defaultdict(list)
        with open(self.file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                for (k,v) in row.items():
                    columns[k].append(v)
        f.close()
        matches = zip(columns['HomeTeam'], columns['AwayTeam'])
        return matches
        
    def get_matches(self, matches):
        match_up = []
        for country in matches:
            if country not in match_up:
                match_up.append(country)
        return match_up
    
    def get_countries(self, matches):
        countries = []
        for nation in matches:
            for country in nation:
                if country not in countries:
                    countries.append(country)
        return countries
       