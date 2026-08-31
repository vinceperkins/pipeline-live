from pipeline_live.engine import LivePipelineEngine
from pipeline_live.data.alpaca.pricing import USEquityPricing
from pipeline_live.data.iex.fundamentals import IEXKeyStats

from pipeline_live.data.alpaca.factors import AverageDollarVolume
from zipline.pipeline import Pipeline


from .datamock import mock_iex
from .datamock import mock_tradeapi


def test_engine(refdata, stocks, alpaca_tradeapi, data_path):
    def list_symbols():
        return ['A', 'AA']

    mock_iex.get_available_symbols(refdata)
    mock_iex.get_key_stats(stocks)
    mock_iex.get_chart(stocks)
    mock_tradeapi.list_assets(alpaca_tradeapi)
    mock_tradeapi.get_bars(alpaca_tradeapi)

    eng = LivePipelineEngine(list_symbols)

    pipe = Pipeline({
        'close': USEquityPricing.close.latest,
    })
    df = eng.run_pipeline(pipe)
    assert df.shape == (2, 1)
    assert df.close['AA'] > 40

    ADV = AverageDollarVolume(window_length=2)
    top1 = ADV.top(1)
    pipe = Pipeline({
        'adv': ADV,
        'close': USEquityPricing.close.latest,
        'marketcap': IEXKeyStats.marketcap.latest,
    }, screen=top1)

    df = eng.run_pipeline(pipe)
    assert sorted(df.columns) == ['adv', 'close', 'marketcap']
    assert df.shape[0] == 1
