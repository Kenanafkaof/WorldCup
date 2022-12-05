import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.module.conversion import Database
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
db = Database()


def combine(team_data, loss_data):
    combined_data = []
    for loss in loss_data:
        data = {
            "opponent": loss[0],
            "probability": loss[1]
        }
        combined_data.append(data)

    for victory in team_data:
        data = {
            "opponent": victory[0][3],
            "probability": victory[0][4]
        }
        combined_data.append(data)
    
    return combined_data

def create_figure(combined_data):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    for team in combined_data:
        print(team)
    xs = [str(team['opponent']) for team in combined_data]
    ys = [float(team['probability']) for team in combined_data]
    axis.plot(xs, ys)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"data:image/png;base64,{data}"

team_data = db.get_victories("Germany"), 
loss_data=db.get_losses("Germany")
data = combine(team_data, loss_data)