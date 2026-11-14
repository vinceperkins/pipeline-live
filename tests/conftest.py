import pytest
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from pipeline_live.data.sources import iex as sources_iex
from pipeline_live.data.sources import alpaca as sources_alpaca


@pytest.fixture
def alpaca_tradeapi():
    with patch.object(sources_alpaca, 'TradingClient') as trading,             patch.object(sources_alpaca, 'StockHistoricalDataClient') as data:
        yield SimpleNamespace(trading=trading, data=data)


@pytest.fixture
def refdata():
    with patch.object(sources_iex, 'refdata') as refdata:
        yield refdata


@pytest.fixture
def stocks():
    with patch.object(sources_iex, 'Stock') as stocks:
        yield stocks


@pytest.fixture
def data_path():
    with patch('zipline.utils.paths.data_path') as data_path:
        with tempfile.TemporaryDirectory() as t:
            data_path.return_value = t
            yield data_path
