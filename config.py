import os
from pathlib import Path


# ----------------------------------------------------------
# --------------- START OF PARAMETERS TO SET ---------------
# ----------------------------------------------------------

pairs = [
    'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'LTCUSDT',
    'XMRUSDT', 'DOTUSDT', 'QTUMUSDT', 'YGGUSDT',
    'LINKUSDT', 'BCHUSDT', 'MANAUSDT', 'ATOMUSDT',
    'RAREUSDT', 'RUNEUSDT', 'ROSEUSDT', 'ALICEUSDT'
]

timeframes = ['1d', '4h', '1h', '15m', '3m']
update_period = '1d'


# ----------------------------------------------------------
# ---------------- END OF PARAMETERS TO SET ----------------
# ----------------------------------------------------------

root_path = Path(os.getcwd())
data_path = root_path / 'data'
ledger_path = data_path / 'ledger.pickle'

raw_ohlc_columns = [
    'open_time', 'open_price', 'high_price', 'low_price', 'close_price', 
    'base_volume', 'close_time', 'quote_volume', 'n_trades', 
    'taker_buy_base_volume', 'taker_buy_quote_volume'
]
ohlc_columns = [
    'open_time', 'close_time', 'open_price', 'high_price', 
    'low_price', 'close_price', 'quote_volume'
]
