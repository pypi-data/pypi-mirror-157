import json
import logging
import time

import pandas as pd
from ccxt.base.exchange import Exchange
from notecoin.base.database import KlineData
from tqdm import tqdm

logger = logging.getLogger()
unix_month = 2678400000


class LoadDataKline:
    def __init__(self, exchange: Exchange, *args, **kwargs):
        self.table = KlineData(source=exchange.name)
        self.exchange = exchange
        super(LoadDataKline, self).__init__(*args, **kwargs)

    def load_all(self, *args, **kwargs):
        self.exchange.load_markets()
        for sym in tqdm(self.exchange.symbols):
            if ':' not in sym:
                self.load(sym, *args, **kwargs)

    def _load(self, symbol, fetch_since, timeframe='1m', limit=100, try_times=3, *args, **kwargs):
        if try_times <= 0:
            return False, None

        try:
            result = self.exchange.fetch_ohlcv(symbol, timeframe, fetch_since, limit=limit)
            result = self.exchange.sort_by(result, 0)
            if len(result) == 0:
                return False, f'result is empty, fetch_since:{fetch_since}'

            df = pd.DataFrame(result, columns=['timestamp', 'open', 'close', 'low', 'high', 'vol'])
            df['symbol'] = symbol
            self.table.insert(json.loads(df.to_json(orient='records')))
            time.sleep(int(self.exchange.rateLimit / 1000))
            return True, result
        except Exception as e:
            return self._load(symbol, fetch_since, timeframe, limit=limit, try_times=try_times - 1, *args, **kwargs)

    def load(self, symbol, unix_start, unix_end, timeframe='1m', limit=100, *args, **kwargs):
        unix_max, unix_min = self.table.select_symbol_maxmin(symbol)
        unix_delta = limit * self.exchange.parse_timeframe(timeframe) * 1000

        unix_start = unix_start
        unix_end = unix_end
        unix_max = unix_max or self.exchange.milliseconds()
        unix_min = unix_min or self.exchange.milliseconds()
        #print(unix_start, unix_end, unix_max, unix_max)

        if unix_min >= unix_start:
            unix_temp = unix_min
            pbar = tqdm(range(unix_min, unix_start, -unix_delta), desc=symbol)
            for _ in pbar:
                status, result = self._load(symbol, unix_temp - unix_delta, timeframe=timeframe, limit=limit)
                if status is False:
                    logger.info("result is null")
                    break
                pbar.set_postfix({'fetch_since': self.exchange.iso8601(result[0][0])})
                unix_temp = result[0][0]

        if unix_max >= unix_end:
            unix_temp = unix_max
            pbar = tqdm(range(unix_max, unix_end, unix_delta), desc=symbol)
            for _ in pbar:
                status, result = self._load(symbol, unix_temp, timeframe=timeframe, limit=limit)
                if status is False:
                    print(result)
                    break
                unix_temp = result[-1][0]
