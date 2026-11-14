import os
from datetime import timedelta

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import Adjustment
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, AssetStatus
from alpaca.trading.requests import GetAssetsRequest

from .util import (
    daily_cache, parallelize
)


def _credentials():
    """Read credentials from the same env vars alpaca-trade-api used."""
    return (
        os.environ.get('APCA_API_KEY_ID'),
        os.environ.get('APCA_API_SECRET_KEY'),
    )


def _trading_client():
    key, secret = _credentials()
    base_url = os.environ.get('APCA_API_BASE_URL', '')
    return TradingClient(key, secret, paper='paper' in base_url)


def _data_client():
    key, secret = _credentials()
    return StockHistoricalDataClient(key, secret)


def list_symbols():
    api = _trading_client()
    assets = api.get_all_assets(GetAssetsRequest(
        status=AssetStatus.ACTIVE,
        asset_class=AssetClass.US_EQUITY,
    ))
    return [a.symbol for a in assets if a.tradable]

def get_stockprices(limit=365, timespan='day'):
    all_symbols = list_symbols()

    @daily_cache(filename='alpaca_chart_{}'.format(limit))
    def get_stockprices_cached(all_symbols):
        return _get_stockprices(all_symbols, limit, timespan)

    return get_stockprices_cached(all_symbols)


def _get_stockprices(symbols, limit=365, timespan='day'):
    '''Get stock data (key stats and previous) from Alpaca.
    Just deal with Alpaca's 200 stocks per request limit.
    '''

    trading = _trading_client()
    data_client = _data_client()
    timeframe = TimeFrame.Minute if timespan == "minute" else TimeFrame.Day
    clock_day = trading.get_clock().timestamp.replace(
        hour=0, minute=0, second=0, microsecond=0)
    start = None

    #Data v1 used to handle this itself, so we have to do it manually now
    if timespan == 'minute':
        start = clock_day - timedelta(minutes=limit)
    else:
        start = clock_day - timedelta(days=limit)

    def fetch(symbols):
        data = {}
        for symbol in symbols:
            bars = data_client.get_stock_bars(StockBarsRequest(
                symbol_or_symbols=symbol,
                start=start,
                limit=limit,
                timeframe=timeframe,
                adjustment=Adjustment.RAW,
            ))
            df = bars.df
            if df.empty:
                df = pd.DataFrame(index=pd.DatetimeIndex([], tz='UTC'))
            else:
                # alpaca-py returns a (symbol, timestamp) MultiIndex
                df = df.droplevel('symbol')

            # Update the index format for comparison with the trading calendar
            if not df.empty:
                if df.index.tzinfo is None:
                    df.index = df.index\
                        .tz_localize('UTC')\
                        .tz_convert('US/Eastern')
                else:
                    df.index = df.index.tz_convert('US/Eastern')


            data[symbol] = df.asfreq('C') if timeframe != 'minute' else df

        return data

    return parallelize(fetch, splitlen=199)(symbols)
