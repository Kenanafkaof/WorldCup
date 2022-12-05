from flask import Flask, redirect, Response, make_response, render_template, request, session, url_for
from flask_cors import CORS, cross_origin
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO
import base64
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.module.conversion import Database

db = Database()
app = Flask(__name__)
CORS(app)
def create_figure(cups):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = [str(team[0]) for team in cups]
    ys = [float(team[1]) for team in cups]
    axis.scatter(xs, ys)
    axis.set_ylabel('World Cups')
    axis.set_xlabel('Country')
    axis.set_title('Number of World Cups')
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"
@app.route('/bracket')
def bracket():
    figure = create_figure(db.get_cups())
    return render_template("bracket.html", round16=db.show_data(), quarters=db.show_quarters(), semis=db.show_semis(), final=db.show_finals(), modal=False, figure=figure)

@app.route("/team" , methods=['GET'])
def teams():
    figure = create_figure(db.get_cups())
    args = request.args
    team = args.get('t')
    return render_template("bracket.html", round16=db.show_data(), quarters=db.show_quarters(), semis=db.show_semis(), final=db.show_finals(), team_data = db.get_victories(team), loss_data=db.get_losses(team), modal=True, team=team, figure=figure)

@app.route("/search" , methods=['POST'])
def search():
    team = request.form.get('team').capitalize()
    valid = db.validate_query(team)

    def combine(team_data, loss_data):
        combined_data = []
        for loss in loss_data:
            data = {
                "opponent": loss[0],
                "probability": loss[1]
            }
            combined_data.append(data)

        for team in team_data:
            for opponent in team:
                data = {
                    "opponent": opponent[3],
                    "probability": opponent[4]
                }
                combined_data.append(data)
        return combined_data

    def create_figure(combined_data):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        xs = [str(team['opponent']) for team in combined_data]
        ys = [float(team['probability']) for team in combined_data]
        axis.scatter(xs, ys)
        axis.set_ylabel('Win Probability')
        axis.set_xlabel('Opponent')
        axis.set_title('Opponent and Probability')
        buf = BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"data:image/png;base64,{data}"

    if valid is True:
        team_data = db.get_victories(team), 
        loss_data=db.get_losses(team)
        data = combine(team_data, loss_data)
        figure = create_figure(data)
        return render_template("team.html", 
            round16=db.show_data(), 
            quarters=db.show_quarters(), 
            semis=db.show_semis(), 
            final=db.show_finals(), 
            team_data = db.get_victories(team), 
            loss_data=loss_data, 
            players=db.get_team(team), 
            team=team, 
            ranking=db.get_standing(team),
            figure = figure
        )
    return render_template("error.html")

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)