from module.conversion import Database, Login
import sqlite3 as sl

<<<<<<< Updated upstream
#data = Database().create_group()
=======
data = Database().parse_world_cups()
>>>>>>> Stashed changes

def clear_data():
    db = Database()
    db.clear_round_16()
    db.clear_quarters()
    db.clear_semis()
    db.clear_final()

#Database().clear_model()
<<<<<<< Updated upstream
#clear_data()

Login().login_create()
=======
#clear_data()
>>>>>>> Stashed changes
