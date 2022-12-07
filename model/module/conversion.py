import sqlite3 as sl
import json
import os.path
import csv    


class Database:
    def __init__(self):
        #gets the relative path of the db and creates a cursor and conn variable for the class 
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_dir = (BASE_DIR + '\\worldcup.db')
        self.conn = sl.connect(db_dir, check_same_thread=False)
        self.curs = self.conn.cursor()

    def show_tables(self):
        #shows all the tables within the db 
        self.curs.execute("SELECT name FROM sqlite_master WHERE type='table';")
 
        myresult = self.curs.fetchall()
        
        for x in myresult:
            print(x)

    #all the delete logic for the database 

    def clear_round_16(self):
        sql = "DELETE FROM round16;"
        self.curs.execute(sql)
        self.conn.commit()

    def clear_quarters(self):
        sql = "DELETE FROM quarters;"
        self.curs.execute(sql)
        self.conn.commit()

    def clear_semis(self):
        sql = "DELETE FROM semis;"

        self.curs.execute(sql)
        self.conn.commit()

    def clear_final(self):
        sql = "DELETE FROM final;"

        self.curs.execute(sql)
        self.conn.commit()

    def clear_model(self):
        sql = "DELETE FROM model;"

        self.curs.execute(sql)
        self.conn.commit()

    #all the getters/setters for the db -> returns the required data 
    
    def show_group(self):
        user_list = self.curs.execute("SELECT * FROM groupstage")    
        result = user_list.fetchall()
        return result

    def show_data(self):
        user_list = self.curs.execute("SELECT * FROM round16")    
        result = user_list.fetchall()
        return result

    def show_quarters(self):
        user_list = self.curs.execute("SELECT * FROM quarters")    
        result = user_list.fetchall()
        return result

    def show_semis(self):
        user_list = self.curs.execute("SELECT * FROM semis")    
        result = user_list.fetchall()
        return result

    def show_finals(self):
        user_list = self.curs.execute("SELECT * FROM final")    
        result = user_list.fetchall()
        return result
    
    def show_probability(self):
        user_list = self.curs.execute("SELECT * FROM model")    
        result = user_list.fetchall()
        return result

    def delete_table(self):
        sql = "DROP TABLE round16"

        self.curs.execute(sql)

    #table creation for db instantiation 

    def table_maker(self, table):
        self.curs.execute('DROP TABLE IF EXISTS round16')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    f'{table} (`home` text, `homeimage` text, `away` text, `awayimage` text)')
        self.conn.commit()

    def create_group(self):
        self.curs.execute('DROP TABLE IF EXISTS round16')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'round16 (`home` text, `homeimage` text, `away` text, `awayimage` text)')
        self.conn.commit()

    def model_create(self):
        self.curs.execute('DROP TABLE IF EXISTS round16')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'cups (`team` text, `count` text)')
        self.conn.commit()

    def create_main(self):
        self.curs.execute('DROP TABLE IF EXISTS round16')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'model (`winner` text, `winnerprobaility` text, `winnerimage` text, `loser` text, `loserprobability` text, `loserimage` text)')
        self.conn.commit()

    def create_players(self):
        self.curs.execute('DROP TABLE IF EXISTS players')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'players (`team` text, `player` text, `position` text)')
        self.conn.commit()

    def create_rankings(self):
        self.curs.execute('DROP TABLE IF EXISTS rankings')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'rankings (`team` text, `position` text)')
        self.conn.commit()
    #showing work -> how were the files/csvs converted into the db 

    def convert_intial(self):
        with open("model/model/dependencies/flags.json") as data:
            data = json.load(data)
            j = 0 
            k = 0
            for country in data:
                image = country['image']
                country = country['country']

    #insertion of data into the model 

    def insert_fixtures(self, home, away, table):
        #creates the url variables which will me changed 
        home_url = ''
        away_url = ''
        #opens and iterates through the flags file in order to get the flag for the passed country
        with open("model/dependencies/flags.json") as data:
            data = json.load(data)
            for country in data:
                if country['country'].lower() == home.lower():
                    home_url = country['image']
                if country['country'].lower() == away.lower():
                    away_url = country['image']

        #depending on the table which is passed, insert the corresponding data in the right spot 
        if table == "round16":
            sql = "INSERT INTO round16 (home, homeimage, away, awayimage) VALUES (?, ?, ?, ?)"      #creates a user based on the username and password parameters and inserts into the db
        elif table == "quarters":
            sql = "INSERT INTO quarters (home, homeimage, away, awayimage) VALUES (?, ?, ?, ?)"      #creates a user based on the username and password parameters and inserts into the db
        elif table == "semis":
            sql = "INSERT INTO semis (home, homeimage, away, awayimage) VALUES (?, ?, ?, ?)"      #creates a user based on the username and password parameters and inserts into the db
        elif table == "final":
            sql = "INSERT INTO final (home, homeimage, away, awayimage) VALUES (?, ?, ?, ?)"      #creates a user based on the username and password parameters and inserts into the db
        
        sql_add = (home, home_url, away, away_url)
        res = self.curs.execute(sql, sql_add)
        self.conn.commit()

    def insert_probability(self, winner, winnerprobability, loser, loserprobability):
        #takes the probability from the model and puts it into the db using the same logic as above with iteration of the flags file
        winner_url = ''
        loser_url = ''
        with open("model/dependencies/flags.json") as data:
            data = json.load(data)
            for country in data:
                if country['country'].lower() == winner.lower():
                    winner_url = country['image']
                if country['country'].lower() == loser.lower():
                    loser_url = country['image']

        sql = "INSERT INTO model (winner, winnerprobaility, winnerimage, loser, loserprobability, loserimage) VALUES (?, ?, ?, ?, ?, ?)"      
        sql_add = (winner, winnerprobability, winner_url, loser, loserprobability, loser_url)
        res = self.curs.execute(sql, sql_add)
        self.conn.commit()


    #all the getters for the frontend -> query database and return data depending on user input/form data 
    def get_victories(self, team):
        team_data = self.curs.execute("SELECT * FROM model WHERE winner = ?", (team,))
        result = team_data.fetchall()
        return result
    
    def get_losses(self, team):
        team_data = self.curs.execute("SELECT * FROM model WHERE loser = ?", (team,))
        result = team_data.fetchall()
        return result

    def get_team(self, team):
        team_data = self.curs.execute("SELECT * FROM players WHERE team = ?", (team,))
        result = team_data.fetchall()
        return result

    def get_standing(self, team):
        team_data = self.curs.execute("SELECT * FROM rankings WHERE team = ?", (team,))
        result = team_data.fetchall()
        return result

    def get_cups(self):
        team_data = self.curs.execute("SELECT * FROM cups")
        result = team_data.fetchall()
        return result
    

    #validate the query that the user is making to make sure that the country/team exists in the db
    #if not, then return False -> this is then interpreted via backend code 
    def validate_query(self, team):
        team_data = self.curs.execute("SELECT * FROM model WHERE winner = ? or loser = ?", (team, team,))
        result = team_data.fetchall()
        if len(result) > 0:
            return True
        return False

    def parse_csv(self):
        with open("model/dependencies/fifa_rankings.csv", 'r', encoding="utf8") as infile:
            reader = csv.DictReader(infile)
            #fieldnames = reader.fieldnames
            for row in reader:
                sql = "INSERT INTO rankings (team, position) VALUES (?, ?)"      
                sql_add = (row['Team'], row['Position'])
                res = self.curs.execute(sql, sql_add)
                self.conn.commit()
                #print(row)  # e.g. `['foo', 'bar']`

    def parse_players(self):
        with open("model/dependencies/players.csv", 'r', encoding="utf8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                squad = row['Squad'].replace("2022 ", "")
                sql = "INSERT INTO players (team, player, position) VALUES (?, ?, ?)"      
                sql_add = (squad, row['Player'], row['Pos'])
                res = self.curs.execute(sql, sql_add)
                self.conn.commit()

    def parse_world_cups(self):
        with open("model/dependencies/WorldCups.csv", 'r', encoding="utf8") as infile:
            reader = csv.DictReader(infile)
            world_cup_count = []
            for row in reader:
                #squad = row['Squad'].replace("2022 ", "")
                #sql = "INSERT INTO players (team, player, position) VALUES (?, ?, ?)"      
                #sql_add = (squad, row['Player'], row['Pos'])
                #res = self.curs.execute(sql, sql_add)
                #self.conn.commit()
                winner = row['Winner']
                if winner == "Germany FR":
                    winner = winner.replace(" FR", "")
                to_append = {
                    "winner": winner,
                    "count": 0
                }
                world_cup_count.append(winner)
            count_dictionary = []
            for team in world_cup_count:
                count = world_cup_count.count(team)
                data = {
                    "team": team,
                    "count": count
                }
                if data not in count_dictionary:
                    sql = "INSERT INTO cups (team, count) VALUES (?, ?)"      
                    sql_add = (team, count)
                    res = self.curs.execute(sql, sql_add)
                    self.conn.commit()  
    def main(self):
        #Database.create_database(self)
        Database.show_tables(self)
        #Database.convert_csv(self)

class Login:
    #logic for the login and various functions for it and user data 
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_dir = (BASE_DIR + '\\worldcup.db')
        self.conn = sl.connect(db_dir, check_same_thread=False)
        self.curs = self.conn.cursor()

    #table creation function and deletion 
    def login_create(self):
        self.curs.execute('DROP TABLE IF EXISTS login')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'authentication (`email` text, `username` text, `password` text)')
        self.conn.commit()

    def delete_table(self):
        sql = "DROP TABLE selectedteam"

        self.curs.execute(sql)
    
    def team_create(self):
        self.curs.execute('DROP TABLE IF EXISTS login')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'selectedteam (`username` text, `team` text, `image` text)')
        self.conn.commit()

    def player_create(self):
        self.curs.execute('DROP TABLE IF EXISTS login')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'selectedplayer (`username` text, `player` text, `team` text)')
        self.conn.commit()

    def flags(self):
        self.curs.execute('DROP TABLE IF EXISTS login')
        self.curs.execute('CREATE TABLE IF NOT EXISTS '
                    'flags (`team` text, `flag` text)')
        self.conn.commit()

    #gets data depending on queries/no queries

    def get_all_teams(self):
        user_list = self.curs.execute("SELECT * FROM flags")
        result = user_list.fetchall()
        return result

    def get_players(self, team):
        team_data = self.curs.execute("SELECT * FROM players WHERE team = ?", (team,))
        result = team_data.fetchall()
        return result

    def validate_team(self, username, team):
        #validates the selected team against db
        team_data = self.curs.execute("SELECT * FROM model WHERE winner = ? or loser = ?", (team, team,))
        result = team_data.fetchall()
        if len(result) > 0:
            #if the result in db, then use following logic: 
            check_query = self.curs.execute("SELECT * FROM selectedteam WHERE username ='%s'" % (username,))
            populate = check_query.fetchall()   #gets the user teams where the username is == username from the POST data
            if len(populate) == 0:              #if there are no results, then create a new entry into the db 
                sql_query = "SELECT * FROM flags WHERE team ='%s'" % (team,)
                res = self.curs.execute(sql_query) 
                result = res.fetchall()  
                home_url = result[0][1]   #based on the results, get the url for the image 
                sql = "INSERT INTO selectedteam (username, team, image) VALUES (?, ?, ?)" 
                sql_add = (username, team, home_url)
                res = self.curs.execute(sql, sql_add)
                self.conn.commit() 
                return home_url
            elif len(populate) > 0:             #if results are found, then UPDATE rather than INSERT 
                sql_query = "SELECT * FROM flags WHERE team ='%s'" % (team,)
                res = self.curs.execute(sql_query) 
                result = res.fetchall() 
                home_url = result[0][1]
                res = self.curs.execute("UPDATE selectedteam SET username = (?), team = (?), image = (?) WHERE username = (?)", (username, team, home_url, username))
                self.conn.commit() 
                return home_url
        return False

    def update_player(self, username, player, team):
        #take the above POST data and add it to the db 
        check_query = self.curs.execute("SELECT * FROM selectedplayer WHERE username ='%s'" % (username,))
        populate = check_query.fetchall()
        #check if the user already had a favorite player -> if they do not, then INSERT | if they do, then UPDATE
        if len(populate) == 0:
            sql = "INSERT INTO selectedplayer (username, player, team) VALUES (?, ?, ?)" 
            sql_add = (username, player, team)
            res = self.curs.execute(sql, sql_add)
            self.conn.commit() 
        elif len(populate) > 0: 
            res = self.curs.execute("UPDATE selectedplayer SET username = (?), player = (?), team = (?) WHERE username = (?)", (username, player, team, username))
            self.conn.commit() 

    #get and set db contents based on the username 

    def get_user_team(self, username):
        team_data = self.curs.execute("SELECT * FROM selectedteam WHERE username = ?", (username,))
        result = team_data.fetchall()
        if len(result) > 0:
            return result
        return False

    def get_user_player(self, username):
        team_data = self.curs.execute("SELECT * FROM selectedplayer WHERE username = ?", (username,))
        result = team_data.fetchall()
        if len(result) > 0:
            return result
        return False


    def create_user(self, email, username, password):
        #takes the POST data from the frontend form and converts it into the DB in order to create a user
        sql_query = "SELECT * FROM authentication WHERE email ='%s'" % (email)
        res = self.curs.execute(sql_query) 
        result = res.fetchall()  
        #validation of the user, if the user is found in the db, then return False which indicated existing user account
        if len(result) == 0:   
            sql = "INSERT INTO authentication (email, username, password) VALUES (?, ?, ?)" 
            sql_add = (email, username, password)
            res = self.curs.execute(sql, sql_add)
            self.conn.commit() 
            return True
        return False

    #backend db for getting, removing, and showing users
    def remove_user(self, email):
        results = self.curs.execute("DELETE FROM authentication WHERE email = ?", (email,)) 
        self.conn.commit() 

    def show_users(self):
        sql_query = "SELECT * FROM authentication" 
        res = self.curs.execute(sql_query) 
        result = res.fetchall() 
    
    def login_authentication(self, username, password):
        #login data for the user if the login is valid, then return TRUE or return FALSE if not
        sql_query = "SELECT * FROM authentication WHERE username ='%s' AND password ='%s'" % (username, password) 
        res = self.curs.execute(sql_query) 
        result = res.fetchall() 
        if len(result) == 0:            
            return False
        else:   
            return True

    def convert_json(self):
        with open("model/dependencies/flags.json") as data:
            data = json.load(data)
            for country in data:
                sql = "INSERT INTO flags (team, flag) VALUES (?, ?)" 
                sql_add = (country['country'], country['image'])
                res = self.curs.execute(sql, sql_add)
                self.conn.commit() 