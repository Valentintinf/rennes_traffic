import plotly.express as px
import numpy as np
import logging


def create_figure(data):

    try:
        if not all(col in data.columns for col in ['traffic', 'lat', 'lon']):
            raise ValueError("Missing required columns in data: 'traffic', 'lat', 'lon'")

        fig_map = px.scatter_mapbox(
            data,
            title="Traffic en temps réel",
            color="traffic",
            lat="lat",
            lon="lon",
            color_discrete_map={'freeFlow':'green', 'heavy':'orange', 'congested':'red'},
            zoom=10,
            height=500,
            mapbox_style="carto-positron"
        )

        return fig_map
    
    except ValueError as value_error:
        logging.error(f"App Utils value - Error: {value_error}")
        raise
    except Exception as error:
        logging.error(f"App Utils create - Error : {error}")
        raise 

def prediction_from_model(model, hour_to_predict):

    try:
        if not 0 <= int(hour_to_predict) <= 23:
            raise ValueError("Hour to predict must be between 0 and 23")

        input_pred = np.array([0] * 24)
        input_pred[int(hour_to_predict)] = 1

        cat_predict = np.argmax(model.predict(np.array([input_pred])))

        return cat_predict

    except ValueError as value_error:
        logging.error(f"App Utils value prediction - Error : {value_error}")
        raise
    except Exception as error:
        logging.error(f"App Utils prediction - Error : {error}")
        raise