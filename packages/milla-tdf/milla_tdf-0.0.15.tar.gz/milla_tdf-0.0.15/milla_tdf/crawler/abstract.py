from copy import copy
import logging
from typing import Callable, Union

import pandas as pd
from milla_tdf.config import TradingFrameWorkConfig
from milla_tdf.crawler.error_codes import CrawlerError
from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData
from enum import Enum
import requests
from dacite import from_dict
from milla_tdf.field_mapping import FieldMappingConfig

class UpdateModeEnum(Enum):
     APPEND = 'APPEND'
     OVERWRITE = 'OVERWRITE'

class AbstractCrawler():
    data_model:AbstractDataModel
    update_mode:UpdateModeEnum
    @classmethod
    def crawl_data(cls, meta_data: AbstractMetaData, **kwargs) -> list[AbstractDataModel]:
        logging.debug(
            f'{cls.data_model.__name__} -> crawl data_model {cls.data_model.__name__}')
    
    @classmethod
    def build_meta_data(cls,old_meta_data:AbstractMetaData, **kwargs)  -> AbstractMetaData:
        pass

    @classmethod
    def call_fiin_api_get(cls,url:str,params:dict) -> str:

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': TradingFrameWorkConfig.fiin_cookie,
            'Connection': 'keep-alive',
            'Origin': 'https://fiintrade.vn',
            'Referer': 'https://fiintrade.vn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }

        response = requests.request("GET", url, headers=headers,params=params)
        
        if(response.status_code == 401):
            logging.error(f'''Please recheck Fiin's session, username, password''')
            raise CrawlerError(f'Unauthorized')

        return response.text

    @classmethod
    def filter_selected_df(cls,df:pd.DataFrame, **kwargs):
        #by default
        return df 
        

    @classmethod
    def construct_data_model_arr(cls,raw_data_arr:list[dict], data_model:AbstractDataModel, mapping_fields:dict) -> list[AbstractDataModel]:
        data_arr = []

        for raw_data in raw_data_arr:
            data ={}
            for mapping_field in mapping_fields.items():
                key = mapping_field[0]
                value = mapping_field[1]

                if(value.__class__ == str):
                    data[value] = raw_data[key]
                elif(value.__class__ == FieldMappingConfig):
                    function:Callable = value.function
                    args:dict = value.args
                    new_field_name:str = value.new_field_name
                    new_args = copy(args)
                    new_args['raw_value'] = raw_data[key]
                    data[new_field_name] = function(new_args)

            data = from_dict(data_class=data_model, data=data)
            data_arr.append(data)

        return data_arr

                

