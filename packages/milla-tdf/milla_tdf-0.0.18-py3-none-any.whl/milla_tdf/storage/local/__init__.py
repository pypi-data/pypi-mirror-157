import logging

import pandas as pd
from milla_tdf.config import TradingFrameWorkConfig
from milla_tdf.crawler.abstract import AbstractCrawler
from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData
from milla_tdf.data_model.stock_price_data import StockPriceMetaData
from milla_tdf.storage.abstract import AbstractStorage
import pyarrow.csv as pv
import pyarrow.parquet as pq
import pyarrow as pa
from os import path

class LocalStorage(AbstractStorage):
    data_folder: str

    @classmethod
    def load_config(cls, data_folder):
        cls.data_folder = data_folder
        TradingFrameWorkConfig.selenium_driver_path = f'{data_folder}/drivers/chromedriver'
        logging.debug(
            f'{cls.__name__} -> loadConfig to folder {cls.data_folder}')

    @classmethod
    def load_data(cls, data_model: AbstractDataModel, meta_data_model:AbstractMetaData =None, crawler: AbstractCrawler = None, **kwargs) ->pd.DataFrame:
        logging.debug(
            f'{cls.__name__} -> loadData data_model {data_model.__name__} ')

        file_path = f'{cls.data_folder}/{data_model.__name__}.parquet'

        if(path.exists(file_path) == True):
            ### load metadata first
            meta_data = cls.load_metadata(file_path=file_path,data_model=AbstractDataModel,meta_data_model=meta_data_model)
            
            local_data = pd.read_parquet(file_path,engine='pyarrow')
            
            crawled_data_df, new_metadata = cls.build_crawl_data_df(data_model=data_model,crawler=crawler,meta_data=meta_data,**kwargs)

            if(meta_data.to_json()== meta_data.to_json() and crawled_data_df.empty == True):
                return crawler.filter_selected_df(local_data, **kwargs)

            union_df =  pd.concat([local_data,crawled_data_df])
            cls.write_parquet(union_df,new_metadata,data_model)

            return crawler.filter_selected_df(union_df, **kwargs)
        else:
            crawled_data_df, new_metadata = cls.build_crawl_data_df(data_model=data_model,crawler=crawler,meta_data=None,**kwargs)
            cls.write_parquet(crawled_data_df,new_metadata,data_model)
            return crawled_data_df
    
    @classmethod
    def write_parquet(cls,df,new_metadata,data_model):
        table = pa.Table.from_pandas(df)

        custom_meta_json = new_metadata.to_json()
        existing_meta = table.schema.metadata
        combined_meta = {
            'json_str'.encode() : custom_meta_json.encode(),
            **existing_meta
        }

        table = table.replace_schema_metadata(combined_meta)

        pq.write_table(table, f'{cls.data_folder}/{data_model.__name__}.parquet')
        
        logging.info(f'write {data_model.__name__} -> metadata {new_metadata}')
    
    @classmethod
    def build_crawl_data_df(cls,data_model: AbstractDataModel,crawler:AbstractCrawler,meta_data:AbstractMetaData, **kwargs)-> tuple[pd.DataFrame,AbstractMetaData]:
        if(crawler != None):
            data = crawler.crawl_data(data_model=data_model,meta_data=meta_data,**kwargs)
            metadata =  crawler.build_meta_data(meta_data,**kwargs)
            return pd.DataFrame(data),metadata
        else:
            return None,None

    @classmethod
    def load_metadata(cls,file_path:str,meta_data_model:AbstractMetaData,  **kwargs) -> AbstractMetaData:
        try:
            
            raw_metadata:dict = pq.read_table(file_path).schema.metadata[b'json_str']
            return meta_data_model.from_json(raw_metadata.decode('UTF-8')) 
        except KeyError:
            return None

    @classmethod
    def save_data(cls, data_model: AbstractDataModel, df: pd.DataFrame):
        logging.debug(
            f'{cls.__name__} -> saveData data_model {data_model.__name__}')
