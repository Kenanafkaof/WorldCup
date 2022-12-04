from module.teams import GetTeams
from module.model import HistoricData
from module.rankings import GetRankings
def main():
    teams = GetTeams("teams-2022.csv")
    data = teams.parse_data()
    teams.get_countries(data)
    teams.get_matches(data)

def rankings():
    rankings = GetRankings()
    data = rankings.get_page()
    dump = rankings.parse_content(data)
    rankings.write_file(dump)

def train():
    teams = GetTeams("teams-2022.csv")
    data = teams.parse_data()
    teams_list = teams.get_countries(data)
    model = HistoricData(teams_list)
    returned_data = model.get_data()
    groups = model.train_data(returned_data)

def model():
    teams = GetTeams("teams-2022.csv")
    data = teams.parse_data()
    teams_list = teams.get_countries(data)
    model = HistoricData(teams_list)
    returned_data = model.get_data()
    groups = model.train_data(returned_data)
    top_16 = model.get_fixtures(groups)
    print("Round of 16")
    teams_retrieved = model.move_on_structure(top_16[0], 3, "round16")
    quarters = model.clean_and_predict(teams_retrieved, groups[0], groups[1])
    quarters_teams = model.move_on_structure(quarters, 1, "quarters")
    print("Quarters results:")
    semi = model.clean_and_predict(quarters_teams, groups[0], groups[1])
    print("Semi results:")
    semi_teams = model.move_on_structure(semi, 1, "semis")
    final = model.clean_and_predict(semi_teams, groups[0], groups[1])
    print("Final result:")
    final_teams = model.move_on_structure(final, 1, "final")
    results = model.clean_and_predict(final_teams, groups[0], groups[1])


if __name__ == "__main__":
    model()
    #rankings()