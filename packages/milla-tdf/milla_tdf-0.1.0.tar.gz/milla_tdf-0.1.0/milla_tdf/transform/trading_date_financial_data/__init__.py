from datetime import timedelta
import pandas as pd

from milla_tdf.transform.error_codes import TransformError

def transform_data(stock_price_df:pd.DataFrame,financial_df:pd.DataFrame,lagging_days:int):

    if('yearReport' not in financial_df or 'lengthReport' not in financial_df):
        raise TransformError(f'Not found field yearReport & lengthReport')

    quarter_series = financial_df['yearReport'].astype(str) +'-Q' + financial_df['lengthReport'].astype(str)

    financial_df['apply_date'] = pd.PeriodIndex(quarter_series, freq='Q').to_timestamp() + timedelta(days=lagging_days + 90)

    stock_price_df = stock_price_df.sort_values('Time')
    financial_df = financial_df.sort_values('apply_date')

    result = pd.merge_asof(left=stock_price_df,right=financial_df,by='Symbol',left_on='Time',right_on='apply_date',direction='backward')

    return result
