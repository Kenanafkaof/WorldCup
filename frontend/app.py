from flask import Flask, redirect, make_response, render_template, request, session, url_for
from flask_cors import CORS, cross_origin
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.module.conversion import Database

db = Database()
app = Flask(__name__)
CORS(app)

@app.route('/bracket')
def bracket():
    return render_template("bracket.html", round16=db.show_data(), quarters=db.show_quarters(), semis=db.show_semis(), final=db.show_finals(), modal=False)

@app.route("/team" , methods=['GET'])
def teams():
    args = request.args
    team = args.get('t')
    return render_template("bracket.html", round16=db.show_data(), quarters=db.show_quarters(), semis=db.show_semis(), final=db.show_finals(), team_data = db.get_victories(team), loss_data=db.get_losses(team), modal=True, team=team)

@app.route("/search" , methods=['POST'])
def search():
    team = request.form.get('team')
    valid = db.validate_query(team)
    if valid is True:
        return render_template("team.html", 
            round16=db.show_data(), 
            quarters=db.show_quarters(), 
            semis=db.show_semis(), 
            final=db.show_finals(), 
            team_data = db.get_victories(team), 
            loss_data=db.get_losses(team), 
            players=db.get_team(team), 
            team=team, 
            ranking=db.get_standing(team)
        )
    if valid is False:
        return render_template("error.html")

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)