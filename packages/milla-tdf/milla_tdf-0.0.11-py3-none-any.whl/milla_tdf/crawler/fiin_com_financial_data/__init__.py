from copy import copy
from datetime import datetime
import json
import logging
from dacite import Config, from_dict
from dateutil.relativedelta import relativedelta
import pandas as pd
from milla_tdf.config import TradingFrameWorkConfig
from milla_tdf.crawler.abstract import AbstractCrawler, UpdateModeEnum
from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData
from milla_tdf.data_model.com_financial_data import ComFinancialData, ComFinancialMetaData
from milla_tdf.data_model.stock_price_data import StockPriceData, StockPriceMetaData

class FiinComFinancialDataCrawler(AbstractCrawler):
    data_model = ComFinancialData
    update_mode = UpdateModeEnum.APPEND
    @classmethod
    def crawl_data(cls, meta_data: ComFinancialMetaData,**kwargs) -> list[StockPriceData]:
        symbols = kwargs['symbols']

        result: list[ComFinancialData] = []
        
        symbol_info_df:pd.DataFrame = kwargs['symbol_info_df']

        for symbol in symbols:
            time_lines = cls.build_timeline_arr(symbol,meta_data,**kwargs)

            if(time_lines == None):
                continue

            logging.info(f'crawl {cls.data_model.__name__} symbol {symbol} timelines {time_lines}')

            organ_code = symbol_info_df[symbol_info_df['Symbol'] == symbol]['OrganCode'].iloc[0]

            logging.debug(f'''symbol {symbol} --> organ_code {organ_code}''')

            url = f'{TradingFrameWorkConfig.fiin_fundamental_end_point}/FinancialAnalysis/GetFinancialRatioV2?language=vi&Type=Company&OrganCode={organ_code}'

            for time_line in time_lines:
                url = f'{url}&Timeline={time_line}'

            response = cls.call_fiin_api_get(url,{})

            logging.info(response)
            raw_data = json.loads(response)['items']

            for data in raw_data:
                if(data['value'] == None):
                    continue
                
                if(data['value']['organCode'] != 'EndOfData'):
                    data['value']['Symbol'] = symbol
                    result.append(from_dict(data_class=ComFinancialData, data=data['value'],config=Config(check_types=False)))

        return result

    @classmethod
    def build_timeline_arr(cls,symbol,old_meta_data:ComFinancialMetaData, **kwargs) -> list[str]:
        try:
            latest_updated = old_meta_data.updated[old_meta_data.symbols.index(symbol)]
        except ValueError :
            latest_updated = TradingFrameWorkConfig.data_start_at
        except AttributeError:
            latest_updated = TradingFrameWorkConfig.data_start_at

        
        if(latest_updated == datetime.now().strftime('%Y-%m-%d')):
            return None
        
        start = datetime.strptime(latest_updated,'%Y-%m-%d')
        end = datetime.now()

        result = []
        while start < end:
            result.append(f'{start.year}_{pd.Timestamp(start).quarter}')
            start = start + relativedelta(months=+3)

        return result

    @classmethod
    def build_meta_data(cls,old_meta_data:ComFinancialMetaData, **kwargs)  -> AbstractMetaData:
        super().build_meta_data(old_meta_data,**kwargs)
        if(old_meta_data == None):
            #build new meta data
            symbols = kwargs['symbols']
            updated = [datetime.now().strftime('%Y-%m-%d') for x in symbols]
            return ComFinancialMetaData(symbols,updated)
        else:
            #update old metadata
            return cls.find_and_update_old_metadata(old_meta_data,**kwargs)

    
    @classmethod
    def find_and_update_old_metadata(cls,old_meta_data:ComFinancialMetaData, **kwargs) -> StockPriceMetaData:
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

        return ComFinancialMetaData(old_symbols,old_updated)

    @classmethod
    def filter_selected_df(cls,df:pd.DataFrame, **kwargs) -> pd.DataFrame:
        symbols = kwargs['symbols']

        return df[df['Symbol'].isin(symbols) ]

