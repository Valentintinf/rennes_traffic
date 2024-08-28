import pandas as pd
import requests
import logging

class GetData(object):

    def __init__(self, url) -> None:
        self.url = url   
        # Error handling for HTTP request and JSON parsing
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.data = response.json()
        except requests.exceptions.RequestException as req_error:
            logging.error(f"App Data request - Error : {req_error}")
            raise
        except ValueError as json_error:
            logging.error(f"App Data JSON - Error : {json_error}")
            raise 

    def processing_one_point(self, data_dict: dict):
        try:
            
            temp = pd.DataFrame({key: [data_dict[key]] for key in ['datetime', 'trafficstatus', 'geo_point_2d', 'averagevehiclespeed', 'traveltime']})
            temp = temp.rename(columns={'trafficstatus': 'traffic'})
            
            temp['lat'] = temp.geo_point_2d.map(lambda x: x['lat'])
            temp['lon'] = temp.geo_point_2d.map(lambda x: x['lon'])
            del temp['geo_point_2d']

        except KeyError as key_error:
            logging.error(f"App Data Key - Error : {key_error}")
            raise 
        except Exception as processing_error:
            logging.error(f"App Data processing - Error : {processing_error}")
            raise

        return temp

    def __call__(self):

        try:
            res_df = pd.DataFrame({})

            for data_dict in self.data:
                temp_df = self.processing_one_point(data_dict)
                res_df = pd.concat([res_df, temp_df])

            res_df = res_df[res_df["traffic"] != 'unknown']

        except Exception as error:
            logging.error(f"App Data processing - Error : {error}")
            raise

        return res_df