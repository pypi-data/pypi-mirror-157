from copy import copy
from datetime import datetime
import json
import logging
from typing import Union

import pandas as pd
from milla_tdf.config import TradingFrameWorkConfig
from milla_tdf.crawler.abstract import AbstractCrawler, UpdateModeEnum
from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData
from milla_tdf.data_model.stock_price_data import StockPriceData, StockPriceMetaData


class FiinStockPriceDataCrawler(AbstractCrawler):
    data_model = StockPriceData
    update_mode = UpdateModeEnum.APPEND
    @classmethod
    def crawl_data(cls, meta_data: AbstractMetaData,**kwargs) -> list[StockPriceData]:
        super().crawl_data(data_model=cls.data_model,meta_data=meta_data)
        symbols = kwargs['symbols']

        result: list[StockPriceData] = []

        for symbol in symbols:
            latest_update_date = cls.get_latest_update_date(meta_data,symbol)

            if(latest_update_date != None):
                cls.call_api_and_append_result(symbol,latest_update_date,datetime.now().strftime('%Y-%m-%d'),result)

        return result

    @classmethod
    def call_api_and_append_result(cls,symbol:str,start:str,end:str, result:list[StockPriceData],**kwargs):
        date_range_arr = cls.split_calling_arr(start,end)

        for date_range in date_range_arr:
            logging.info(f'''calling data {symbol} from {date_range['start']} -> {date_range['end']}''')

            raw_data = json.loads(cls.call_fiin_api_get(f'{TradingFrameWorkConfig.fiin_technical_end_point}/TradingView/GetStockChartData',
                {'language':'vi','Code':symbol,'Frequency':'Daily',
                    'From':date_range['start'],
                    'To':date_range['end'],
                    'Type':'Stock'
                }
            ))['items']

            for data in raw_data:
                result.append(StockPriceData(symbol,data['tradingDate'],data['openPrice'],data['highestPrice'],data['lowestPrice'],data['closePrice'],data['totalMatchVolume']))
        
    @classmethod
    def split_calling_arr(cls,start:str,end:str):
        start = datetime.strptime(start,'%Y-%m-%d')
        end = datetime.strptime(end,'%Y-%m-%d')

        result = []

        while start < end:
            result.append({'start':start.strftime('%Y-%m-%dT%H:%M:%SZ'),'end':copy(start).replace(year=(start.year) + 1).strftime('%Y-%m-%dT%H:%M:%SZ')})
            start = start.replace(year=(start.year) + 1)

        return result

    @classmethod
    def get_latest_update_date(cls,old_meta_data:StockPriceMetaData,symbol:str, **kwargs)  -> Union[str,None]:
        if(old_meta_data == None):
            return TradingFrameWorkConfig.data_start_at
        try:
            updated = old_meta_data.updated[old_meta_data.symbols.index(symbol)] 

            if(updated == datetime.now().strftime('%Y-%m-%d') ):
                return None
            else:
                return updated
        except ValueError:
            pass

        return TradingFrameWorkConfig.data_start_at

    @classmethod
    def build_meta_data(cls,old_meta_data:StockPriceMetaData, **kwargs)  -> AbstractMetaData:
        super().build_meta_data(old_meta_data,**kwargs)
        if(old_meta_data == None):
            #build new meta data
            symbols = kwargs['symbols']
            updated = [datetime.now().strftime('%Y-%m-%d') for x in symbols]
            return StockPriceMetaData(symbols,updated)
        else:
            #update old metadata
            return cls.find_and_update_old_metadata(old_meta_data,**kwargs)

    
    @classmethod
    def find_and_update_old_metadata(cls,old_meta_data:StockPriceMetaData, **kwargs) -> StockPriceMetaData:
        old_symbols = old_meta_data.symbols
        old_updated = old_meta_data.updated
        updated_symbols = kwargs['symbols']
        new_symbols = []
        update_indexes = []
        for symbol in updated_symbols:
            try:
                update_indexes.append(old_symbols.index(symbol))
            except ValueError:
                new_symbols.append(symbol)
        
        if(len(update_indexes) != 0):
            for update_index in update_indexes:
                old_updated[update_index] = datetime.now().strftime('%Y-%m-%d')

        if(len(new_symbols) != 0):
            for new_symbol in new_symbols:
                old_symbols.append(new_symbol)
                old_updated.append(datetime.now().strftime('%Y-%m-%d'))

        return StockPriceMetaData(old_symbols,old_updated)

    @classmethod
    def filter_selected_df(cls,df:pd.DataFrame, **kwargs) -> pd.DataFrame:
        logging.info('filter')
        symbols = kwargs['symbols']

        return df[df['Symbol'].isin(symbols) ]

