# BINANCE TRACKER

# Augustin BRISSART
# GitHub: @augustin999

# June 2021

import numpy as np
import pandas as pd
import time as tm
import logging

try:    
    from tracker import Binance_API
except:
    import Binance_API

logger = logging.getLogger('tracker')
logger.setLevel(logging.DEBUG)


def pull_historical_data():
    """
    Download all available historical data until now
    """
    logger.info('Pulling all available historical data')

    return


def continue_recurrent_algorithm():
    """
    Appending all data available from latest previously loaded timestamp, until now.
    """

    return