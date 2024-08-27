from flask import Flask, render_template, request
import flask_monitoringdashboard as dashboard
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import logging


from keras.models import load_model

from src.get_data import GetData
from src.utils import create_figure, prediction_from_model 

app = Flask(__name__)

logging.getLogger('werkzeug').level = 40

logger = logging.getLogger(__name__)
logging.basicConfig(filename='errorlogs.log', encoding='utf-8', filemode='a', format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M", level=logging.ERROR)

dashboard.config.init_from(file='config.cfg')

data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
data = data_retriever()

model = load_model('model.h5') 

@app.route('/', methods=['GET', 'POST'])
def index():
    try :
        if request.method == 'POST':
            fig_map = create_figure(data)
            graph_json = fig_map.to_json()

            selected_hour = request.form['hour']
            cat_predict = prediction_from_model(model, selected_hour)

            color_pred_map = {0:["Prédiction : Libre", "green"], 1:["Prédiction : Dense", "orange"], 2:["Prédiction : Bloqué", "red"]}

            return render_template('index.html', graph_json=graph_json, text_pred=color_pred_map[cat_predict][0], color_pred=color_pred_map[cat_predict][1])

        else:
            fig_map = create_figure(data)
            graph_json = fig_map.to_json()

            return render_template('index.html', graph_json=graph_json)
    except Exception as error:
        logging.error(f'App - Error : {error}')

dashboard.bind(app)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as critical:
        logging.critical(f'App crashed - Not launched : {critical}')
