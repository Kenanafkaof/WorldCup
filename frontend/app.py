from email import message
import flask
from flask import Flask, redirect, Response, make_response, render_template, request, session, url_for
from flask_cors import CORS, cross_origin
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO
import base64
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.module.conversion import Database, Login

#instantiates classes for functionality in the app
db = Database()
authentication = Login()

app = Flask(__name__)
CORS(app) #uses CORS for js queries 

#universal function to create the figure based on the amount of cups
def create_figure(cups):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    #indexes for the x and y axis based on the db query 
    xs = [str(team[0]) for team in cups]
    ys = [float(team[1]) for team in cups]
    axis.bar(xs, ys)
    #sets the details of the graph
    axis.set_ylabel('World Cups')
    axis.set_xlabel('Country')
    axis.set_title('Number of World Cups')
    #using bytes, converts the figure into base64 which can be rendered to the frontend 
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"

@app.route('/')
def enter():
    return redirect(url_for('bracket'))

@app.route('/bracket')
def bracket():
    #session checking -> if the user is logged in, display details -> if not dont 
    if 'username' in session:
        return render_template("bracket.html", 
            round16=db.show_data(), 
            quarters=db.show_quarters(), 
            semis=db.show_semis(), 
            final=db.show_finals(), 
            modal=False, 
            username=session['username'],
            check=True,
            figure=create_figure(db.get_cups()))
    else:
        return render_template("bracket.html", 
            round16=db.show_data(), 
            quarters=db.show_quarters(), 
            semis=db.show_semis(), 
            final=db.show_finals(), 
            modal=False, 
            figure=create_figure(db.get_cups()))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    #gets the args from the request (username and password) then submits that data to the database authentication which returns True or False -> this dictates redirect (302)
    username = request.form.get('username')
    password = request.form.get('password')
    validation = authentication.login_authentication(username, password)
    if validation is True:
        session['username'] = username
        return redirect(url_for('.dashboard', username=username)) 
    if validation is False:
        return render_template('login.html', message="Invalid credentials")

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/create', methods=['POST'])
def create():
    #adds a new user based on the inputted form data 
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    #db call for adding the user -> if returns False, then the user exists -> if returns True, then the user is newly created and redirect to the dashboard 
    validation = authentication.create_user(email, username, password)
    if validation is True:
        session['username'] = username
        return redirect(url_for('.dashboard', username=username, email=email)) 
    if validation is False:
        return render_template('signup.html', message="User already exists")


@app.route('/updateteam', methods=['POST'])
def updateteam():
    if 'username' in session:
        loggedIn = True
        username = request.form.get('username')
        team = request.form.get('team')
        #updates the team of the user and validates it within the db -> then returns and displays this data on the frontend 
        team_update = authentication.validate_team(username, team)
        return render_template('dashboard.html', 
            username=username, 
            team=authentication.get_user_team(username), 
            player=authentication.get_user_player(username), 
            countries=authentication.get_all_teams(),
            check=loggedIn)
    else:
        return render_template('login.html')

@app.route('/updateplayer', methods=['POST'])
def updateplayer():
    #checks session to ensure that the user is logged in 
    if 'username' in session:
        loggedIn = True
        username = request.form.get('username')
        team = request.form.get('team')
        player = request.form.get('player')
        #updates the player in the db based on the form data 
        team_update = authentication.update_player(username, player, team)
        return render_template('dashboard.html', 
            username=username, 
            team=authentication.get_user_team(username),
            player=authentication.get_user_player(username), 
            countries=authentication.get_all_teams(),
            check=loggedIn)
    else:
        return render_template('login.html')

@app.route('/getplayers', methods=['POST'])
def getplayers():
    #get request which displays the players for the user -> assumes that they are logged in -> if not, return to log in page 
    if 'username' in session:
        username = session['username']
        loggedIn = True
        team = request.form.get('team')
        return render_template('dashboard.html', 
            username=username, 
            team=authentication.get_user_team(username), 
            player=authentication.get_user_player(username), 
            countries=authentication.get_all_teams(),
            check=loggedIn,
            players = authentication.get_players(team),
            show=True,
            selected_team=team
        )
    else:
        return render_template('login.html') 
@app.route('/dashboard')
def dashboard():
    #this is the main redirect request which is made for login authentication and in order to display the profile -> assumes an existing session is found 
    if 'username' in session:
        loggedIn = True
        username = session['username']
        player=authentication.get_user_player(username), 
        print(player)
        return render_template('dashboard.html', 
            username=username, 
            check=loggedIn, 
            team=authentication.get_user_team(username),
            player=authentication.get_user_player(username), 
            countries=authentication.get_all_teams()
        )
    else:
        return render_template('login.html')

@app.route("/team" , methods=['GET'])
def teams():
    #get the form data and create a figure for the particular team 
    team = request.args.get('t')
    figure = create_figure(db.get_cups())
    #conditional rendering if the user is logged in or not 
    if 'username' in session:
        return render_template("bracket.html", 
            round16=db.show_data(), 
            quarters=db.show_quarters(), 
            semis=db.show_semis(), 
            final=db.show_finals(), 
            team_data = db.get_victories(team), 
            loss_data=db.get_losses(team), 
            modal=True, 
            team=team, 
            figure=figure,
            check=True,
            username=session['username']
        )
    else:
        return render_template("bracket.html", 
            round16=db.show_data(), 
            quarters=db.show_quarters(), 
            semis=db.show_semis(), 
            final=db.show_finals(), 
            team_data = db.get_victories(team), 
            loss_data=db.get_losses(team), 
            modal=True, 
            team=team, 
            figure=figure)

@app.route("/search" , methods=['GET', 'POST'])
def search():
    #checks the method -> if it is a POST request, then get form data -> if it is a GET request, then get the args 
    if flask.request.method == 'POST':
        team = request.form.get('team').capitalize()
    elif flask.request.method == 'GET':
        team = request.args.get('team')

    #validate to ensure that the team does exist 
    valid = db.validate_query(team)

    def combine(team_data, loss_data):
        #combines all the data of opponent victory and losses into a single list 
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
        #creates a figure based on the win probability which is passed in as a parameter from the above function 
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
        
    #if the team has been found, then return the valid queries to get the team data and combine it in order to display the figure and that team's players/wins 
    #else return an error page as the team has not been found and the query is not valid 
    if valid is True:
        team_data = db.get_victories(team), 
        loss_data=db.get_losses(team)
        data = combine(team_data, loss_data)
        figure = create_figure(data)
        if 'username' in session:
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
                figure = figure,
                check=True,
                username=session['username']
            )
        else:
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
    else:
        return render_template("error.html")

@app.route('/logout', methods=['POST'])
def logout():
    #logs the user out of the app 
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('.bracket', check = False)) 
    else:
        return render_template('login.html')



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)