import numpy as np
import pandas as pd
import pickle
import os
from pathlib import Path

from pathy import file

import config, spot_api


def build_file_name(pair, tf):
    file_name = f"{pair.upper()}{tf.lower()}.csv"
    return file_name


def ts_ledger_exists():
    """
    Return true if ./data/ledger.pickle already exists, else False.
    """
    return config.ledger_path.exists()


def make_ts_ledger():
    """
    Create ./data/ledger.pickle file
    """
    ledger = dict()
    for pair in config.pairs:
        pair_dict = dict()
        for tf in config.timeframes:
            pair_dict[tf.lower()] = None
        ledger[pair.upper()] = pair_dict
    pickle.dump(ledger, open(config.ledger_path, 'wb'))
    return


def update_ts_ledger(pair, tf, ts):
    ledger = pickle.load(open(config.ledger_path, 'rb'))
    ledger[pair.upper()][tf.lower()] = ts
    pickle.dump(ledger, open(config.ledger_path, 'wb'))
    return


def data_dir_exists():
    """
    Return true if ./data/ folder already exists, else False.
    """
    return config.data_path.exists()


def pair_data_dir_exists(pair):
    """
    Return true if ./data/{pair}/ folder already exists, else False.
    """
    pair_data_path = config.data_path / pair.upper()
    return pair_data_path.exists()


def make_data_dir():
    if data_dir_exists():
        return
    os.mkdir(config.data_path)
    return


def make_pair_data_dir(pair):
    if pair_data_dir_exists(pair):
        return
    pair_data_path = config.data_path / pair.upper()
    os.mkdir(pair_data_path)
    return


def tf_pair_data_exists(pair, tf):
    file_name = build_file_name(pair, tf)
    tf_pair_data_path = config.data_path / pair.upper() / file_name
    return tf_pair_data_path.exists()


def store_data(pair, tf, data):
    file_name = build_file_name(pair, tf)
    pair_tf_data_path = config.data_path / pair.upper() / file_name
    ts = data['open_time'].max()
    update_ts_ledger(pair, tf, ts)
    data.to_csv(pair_tf_data_path, sep=',', index=False)
    return


def get_most_recent_klines(pair, tf):
    ohlc = spot_api.get_klines(pair.lower(), tf.lower())
    ohlc = pd.DataFrame(ohlc, columns=config.raw_ohlc_columns)
    ohlc.sort_values(by='open_time', inplace=True)
    ohlc = ohlc.iloc[:len(ohlc)-1].copy()
    ohlc = ohlc[config.ohlc_columns].copy()
    return ohlc


def get_klines_until_ts(pair, tf, end_ts):
    ohlc = spot_api.get_klines(pair.lower(), tf.lower(), endTime=end_ts)
    ohlc = pd.DataFrame(ohlc, columns=config.raw_ohlc_columns)
    ohlc.sort_values(by='open_time', inplace=True)
    ohlc = ohlc[config.ohlc_columns].copy()
    return ohlc


def get_klines_from_ts(pair, tf, start_ts):
    ohlc = spot_api.get_klines(pair.lower(), tf.lower(), startTime=start_ts)
    ohlc = pd.DataFrame(ohlc, columns=config.raw_ohlc_columns)
    ohlc.sort_values(by='open_time', inplace=True)
    ohlc = ohlc[config.ohlc_columns].copy()
    ohlc = ohlc.iloc[1:len(ohlc)-1].copy()
    return ohlc




