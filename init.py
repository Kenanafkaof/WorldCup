from model.module.conversion import Database, Login

db = Database()
login = Login()

def welcome():
    db.table_maker("round16")
    db.table_maker("quarters")
    db.table_maker("semis")
    db.table_maker("final")
    db.model_create()

    