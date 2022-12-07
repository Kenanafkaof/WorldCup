from model.module.conversion import Database, Login
from model.tests import model

#instantiates the various variables corresponding to the class
db = Database()
login = Login()

def welcome():
    #creates all the required tables for the database
    db.create_players()
    db.create_rankings()
    db.table_maker("round16")
    db.table_maker("quarters")
    db.table_maker("semis")
    db.table_maker("final")
    db.create_main()
    db.model_create()
    db.create_group()

    #cleans the data to ensure that all columns are empty and ready for injections

    def clear_data():
        db = Database()
        db.clear_round_16()
        db.clear_quarters()
        db.clear_semis()
        db.clear_final()
    
    #calls the clearing function 
    clear_data()
    #instantiates and runs the model -> which will then insert the data into the DB 
    model()
    db.parse_world_cups()
    db.parse_players()
    db.parse_csv()

    #creates the required user fields such as login authentication as well as required data for dashboard display
    login.login_create()
    login.team_create()
    login.player_create()
    login.flags()
    login.convert_json()
    

if __name__ == "__main__":
    welcome()