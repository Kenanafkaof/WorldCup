from module.conversion import Database
import sqlite3 as sl

data = Database().create_group()

def clear_data():
    db = Database()
    db.clear_round_16()
    db.clear_quarters()
    db.clear_semis()
    db.clear_final()

Database().clear_model()
clear_data()