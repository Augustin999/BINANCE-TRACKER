import numpy as np
import pandas as pd
import pickle
import os
import time as tm
from pathlib import Path

import data_manager, config


def initiate_data(pair, tf):
    """
    No pair data stored before. Pull as much data as possible for that pair.
    """
    # Get most recent data
    data = data_manager.get_most_recent_klines(pair, tf)
    # Then pull older data as long as there is still data to pull
    oldest_ts = int(data['open_time'].min())
    keep_going = True
    while keep_going:
        more_data = data_manager.get_klines_until_ts(pair, tf, oldest_ts)
        if len(more_data) > 1:
            data = data.append(more_data, ignore_index=True)
            oldest_ts = int(data['open_time'].min())
        else:
            keep_going = False
    # Finally, sort_data and save it
    data.drop_duplicates(inplace=True)
    data.sort_values(by='open_time', inplace=True)
    data['close_time'] = data['open_time'] + int(pd.Timedelta(tf.upper()).total_seconds() * 1000)
    data_manager.store_data(pair, tf, data)
    return


if __name__ == '__main__':
    # Check if data_dir exists. If not, create it.
    if not data_manager.data_dir_exists():
        data_manager.make_data_dir()
        data_manager.make_ts_ledger()
    # Check if ledger.pickle exists. If not, create it.
    if not data_manager.ts_ledger_exists():
        data_manager.make_ts_ledger()

    # Check if pair_data_dir exists. If not, create it and pull as much data as possible for each timeframe.
    for pair in config.pairs:
        if not data_manager.pair_data_dir_exists(pair):
            data_manager.make_pair_data_dir(pair)
            for tf in config.timeframes:
                initiate_data(pair, tf)
        # Now, handle the case if new tf have been added to config.timeframes
        else:
            for tf in config.timeframes:
                if not data_manager.tf_pair_data_exists(pair, tf):
                    initiate_data(pair, tf)

    # Now: pair_data_dir and each tf file exist for each pair
    # Case: update pair_data_dir if latest stored open_time is over 2 days old
    ledger = pickle.load(open(config.ledger_path, 'rb'))
    current_time = int(tm.time()*1000)
    for pair in config.pairs:
        for tf in config.timeframes:
            latest_ts = ledger[pair.upper()][tf.lower()]
            if np.abs(current_time - latest_ts) > pd.Timedelta(config.update_period.upper()).total_seconds:
                # Load data that is already stored
                file_name = data_manager.build_file_name(pair, tf)
                file_path = config.data_path / pair.upper() / file_name
                previous_data = pd.read_csv(file_path, sep=',')
                # Pull latest missing data
                new_data = data_manager.get_klines_from_ts(pair, tf, latest_ts)
                # Clean it and append it to previous_data
                previous_data = previous_data.append(new_data, ignore_index=True)
                previous_data.drop_duplicates(inplace=True)
                previous_data.sort_values(by='open_time', inplace=True)
                previous_data['close_time'] = previous_data['open_time'] + int(pd.Timedelta(tf.upper()).total_seconds() * 1000)
                # Store augmented dataset
                data_manager.store_data(pair, tf, previous_data)

    
