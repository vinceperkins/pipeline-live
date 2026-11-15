from datetime import timedelta
from alpaca_trade_api import TimeFrame, REST
import pandas as pd
from .util import (
    daily_cache, parallelize
)


def list_symbols():
    api = REST()
    return [a.symbol for a in api.list_assets(status="active", asset_class ="us_equity") if a.tradable]

def get_stockprices(limit=365, timespan='day'):
    all_symbols = list_symbols()

    @daily_cache(filename='alpaca_chart_{}'.format(limit))
    def get_stockprices_cached(all_symbols):
        return _get_stockprices(all_symbols, limit, timespan)

    return get_stockprices_cached(all_symbols)

def _get_stockprices(symbols, limit=365, timespan='day'):
    api = REST()
    timeframe = TimeFrame.Minute if timespan == "minute" else TimeFrame.Day
    start = None
    def fetch(symbols):
        start = (pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=int(limit * 1.6))).date().isoformat()
        bars = api.get_bars(symbols, timeframe, start=start, adjustment='raw').df
        data = {}
        if bars.empty:
            return data

        # Make sure we have a DatetimeIndex
        if not isinstance(bars.index, pd.DatetimeIndex):
            bars = bars.set_index('timestamp')
        bars.index = pd.to_datetime(bars.index, utc=True)

        for symbol, df in bars.groupby('symbol'):
            df = df.drop(columns='symbol').tail(limit)
            if df.empty:
                continue
            df.index = df.index.normalize()
            df = df[~df.index.duplicated(keep='last')]
            data[symbol] = df.asfreq('C') if timeframe != 'minute' else df
        return data

    return parallelize(fetch, splitlen=199)(symbols)


