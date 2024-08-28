from flask import Flask, render_template, request
import flask_monitoringdashboard as dashboard
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import pandas as pd
import logging
import requests

from keras.models import load_model

from src.get_data import GetData
from src.utils import create_figure, prediction_from_model 

app = Flask(__name__)

logging.getLogger('werkzeug').setLevel(logging.ERROR) 

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename='errorlogs.log',
    encoding='utf-8',
    filemode='a',
    format="{asctime} - {levelname} - {message}", 
    style="{", datefmt="%Y-%m-%d %H:%M", 
    level=logging.ERROR
)

dashboard.config.init_from(file='config.cfg')

try:
    data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
    data = data_retriever()
    if data.empty:
        raise ValueError("App Data empty")
except requests.RequestException as req_error:
    logger.critical(f"App Data retrieve - RequestException - Critical : {req_error}")
    raise RuntimeError("Critical failure: Unable to fetch traffic data --> Leaving the app.") from req_error
except Exception as data_error:
    logger.critical(f"App Data retrieve - General Error - Critical : {data_error}")
    raise RuntimeError("Critical failure: Unable to process traffic data --> Leaving the app") from data_error

try :
    model = load_model('model.h5')
except Exception as critical:
    logger.critical(f"App cannot load model - Critical : {critical}")
    raise RuntimeError("Critical failure : Unable to load model --> Leaving the app.") from critical


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':         
        try:
            fig_map = create_figure(data)
            graph_json = fig_map.to_json()
        except Exception as figure_error:
            logging.error(f"App creating figure - Error : {figure_error}")

        try:
            selected_hour = request.form['hour']
            if not selected_hour.isdigit() or not (0 <= int(selected_hour) <= 23):
                raise ValueError("Invalid hour input. Must be a number between 0 and 23.")
        except ValueError as value_error:
            logging.error(f"App value - Error : {value_error}")
        
        try:
            cat_predict = prediction_from_model(model, selected_hour)
        except Exception as model_error:
            logging.error(f"App Prediction - Error : {model_error}")
        
        color_pred_map = {0:["Prédiction : Libre", "green"], 1:["Prédiction : Dense", "orange"], 2:["Prédiction : Bloqué", "red"]}

        return render_template('index.html', graph_json=graph_json, text_pred=color_pred_map[cat_predict][0], color_pred=color_pred_map[cat_predict][1])

    else:
        try:
            fig_map = create_figure(data)
            graph_json = fig_map.to_json()
        except Exception as figure_error:
            logging.error(f"App get request - Error : {figure_error}")

        return render_template('index.html', graph_json=graph_json)


dashboard.bind(app)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as critical:
        logging.critical(f'App crashed - Critical : {critical}')
