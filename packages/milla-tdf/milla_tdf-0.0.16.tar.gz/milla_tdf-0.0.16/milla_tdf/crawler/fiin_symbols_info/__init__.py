from datetime import datetime
import logging

import pandas as pd
from milla_tdf.config import TradingFrameWorkConfig
from milla_tdf.crawler.abstract import AbstractCrawler, UpdateModeEnum
from milla_tdf.data_model.abstract import AbstractDataModel, AbstractMetaData
from milla_tdf.data_model.stock_price_data import StockPriceData, StockPriceMetaData
from milla_tdf.data_model.symbols_info import SymbolInfoData, SymbolInfoMetaData
from milla_tdf.field_mapping import FieldMappingConfig,remap_data_value
import json

class FiinSymbolsInfoCrawler(AbstractCrawler):
    data_model = SymbolInfoData
    update_mode = UpdateModeEnum.OVERWRITE
    @classmethod
    def crawl_data(cls, meta_data: SymbolInfoMetaData,**kwargs) -> list[SymbolInfoData]:
        super().crawl_data(data_model=cls.data_model,meta_data=meta_data)
        if(meta_data != None and meta_data.updated == datetime.now().strftime('%Y-%m-%d')):
            logging.info(f'skip crawling {cls.__name__}, loaded from local')
            return []

        raw_data = json.loads(cls.call_fiin_api_get(f'{TradingFrameWorkConfig.fiin_core_end_point}/Master/GetListOrganization',{'language':'vi'}))['items']

        data: list[SymbolInfoData]= cls.construct_data_model_arr(raw_data,SymbolInfoData,
            {
                'organCode':'OrganCode',
                'ticker':'Symbol',
                'comTypeCode':'ComTypeCode',
                'comGroupCode': FieldMappingConfig(
                    new_field_name='Board',
                    function=remap_data_value,
                    args = {
                        'mapping_data': {
                            'VNINDEX':'HSX',
                            'UpcomIndex':'UPCOM',
                            'HNXIndex':'HNX'
                        }
                    },
                )
            })

        return data

    @classmethod
    def build_meta_data(cls,old_meta_data:AbstractMetaData, **kwargs) -> SymbolInfoData:
        return SymbolInfoMetaData(updated=datetime.now().strftime('%Y-%m-%d'))

        




