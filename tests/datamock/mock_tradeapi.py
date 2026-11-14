from datetime import datetime, timezone
from types import SimpleNamespace

from alpaca.data.models.bars import BarSet
from alpaca.trading.models import Asset


def list_assets(tradeapi):
    tradeapi.trading().get_all_assets.return_value = [
        Asset(**{'asset_class': 'us_equity',
                 'exchange': 'NYSE',
                 'id': '3ca0202f-01f4-41a0-bb0c-c8864e767ebd',
                 'status': 'active',
                 'symbol': 'AA',
                 'tradable': True,
                 'class': 'us_equity',
                 'marginable': True,
                 'shortable': True,
                 'fractionable': True}),
        Asset(**{'asset_class': 'us_equity',
                 'exchange': 'NYSE',
                 'id': '7595a8d2-68a6-46d7-910c-6b1958491f5c',
                 'status': 'active',
                 'symbol': 'A',
                 'tradable': True,
                 'class': 'us_equity',
                 'marginable': True,
                 'shortable': True,
                 'fractionable': True}),
    ]
    tradeapi.trading().get_clock.return_value = SimpleNamespace(
        timestamp=datetime(2022, 3, 1, 15, 0, tzinfo=timezone.utc))


def get_bars(tradeapi):
    tradeapi.data().get_stock_bars.return_value = BarSet({
        'AA': [
            {
                "t": "2022-02-28T05:00:00Z",
                "o": 163.14,
                "h": 165.4,
                "l": 162.46,
                "c": 165.28,
                "v": 1386252,
                "n": 14053,
                "vw": 164.070877
            }
        ]
    })
