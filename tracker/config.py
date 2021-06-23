# BINANCE TRACKER

# Augustin BRISSART
# GitHub: @augustin999

# June 2021


import os
from pathlib import Path
from pathy import Pathy

try:
    from tracker import env
except:
    import env

if env.is_local():
    root = Path(os.getcwd())
    root = root.parent if root.name != 'SSX999_HEDGE' else root

    data_path = root / 'data'
    

else:
    gcs_bucket = env.get_var('GCP_BUCKET')
    bucket_dir = Pathy(f'gs://{gcs_bucket}')

    data_path = bucket_dir / 'data'
    

# ****************** START OF PARAMETERS TO SET ****************** #
SPOT_UNIVERSE = ['BTCUSDT', 'ETHUSDT', 'QTUMUSDT', 'DOTUSDT', 'ADAUSDT', 'XVSUSDT', 'INJUSDT', 
    'BNBUSDT', 'XRPUSDT', 'LINKUSDT', 'THETAUSDT', 'LTCUSDT', 'ETCUSDT', 'EOSUSDT', 'KSMUSDT',
    'BCHUSDT', 'RUNEUSDT', 'AAVEUSDT', 'BAKEUSDT', 'UNIUSDT', 'XLMUSDT', 'ZECUSDT', 'XMRUSDT',
    'WAVESUSDT', 'ATOMUSDT', 'ALGOUSDT', 'BATUSDT', 'PAXGUSDT'
]
PERPETUAL_UNIVERSE = ['BTCUSDT', 'ADAUSDT', 'XRPUSDT', 'XLMUSDT', 'BZRXUSDT', 'EOSUSDT', 'BATUSDT',
    'ALGOUSDT', 'DOTUSDT', 'BAKEUSDT', 'LINKUSDT', 'KNCUSDT', 'QTUMUSDT', 'UNIUSDT', 'ATOMUSDT', 
    'ETHUSDT', 'LTCUSDT', 'AAVEUSDT', 'XMRUSDT'
]
TIMEFRAMES = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '12h', '1d']
# ******************* END OF PARAMETERS TO SET ******************* #

CSV_SEP = ','
OHLC_COLUMNS = [
    'open_time',
    'open_price',
    'high_price',
    'low_price',
    'close_price',
    'volume',
    'close_time',
    'quote_volume',
    'number_of_trades',
    'taker_buy_volume',
    'taker_buy_quote_volume',
]