import requests
from bs4 import BeautifulSoup
import csv

class GetRankings:
    def __init__(self) -> None:
        #nothing to init here, simply scraping data and converting to the fifa_rankings.csv
        pass

    def get_page(self):
        #get the contents from the webpage and validates response
        content = requests.request("GET", "https://us.soccerway.com/teams/rankings/fifa/?ICID=TN_03_05_01")
        if content.status_code != 200:
            print(content.text)
            return False
        return content

    def parse_content(self, response):
        #finds the corresponding table headers in the html and appends it to a list which can then be returned into a CSV file 
        soup = BeautifulSoup(response.content, 'html.parser')
        rankings = []
        teams = soup.find_all("td", class_="text team")
        score = soup.find_all("td", class_="points")
        rank = soup.find_all("td", class_="rank")
        for ranking, team, scores in zip(rank, teams, score):
            data_append = ranking.get_text(), team.get_text(), round(float(scores.get_text()))
            rankings.append(data_append)
        return rankings

    def write_file(self, rankings):
        #parsing into the CSV file 
        header = ['Position', 'Team', 'Points']
        with open('dependencies/fifa_rankings.csv', 'w', newline='') as outcsv:
            writer = csv.writer(outcsv, delimiter=',')
            writer.writerow(i for i in header)
            for team in rankings:
                writer.writerow(team)