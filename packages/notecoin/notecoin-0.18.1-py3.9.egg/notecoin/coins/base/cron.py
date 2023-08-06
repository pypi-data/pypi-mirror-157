import logging
import os
from datetime import datetime, timedelta

from ccxt import Exchange
from notecoin.coins.base.load import LoadDataKline
from notefile.compress import tarfile

logger = logging.getLogger()


def load_month(exchange: Exchange, tmp_path, timeframe='1m'):
    exchan = LoadDataKline(exchange)
    for i in range(1, 10):
        today = datetime.today()
        month_index = 1

        unix_start = datetime(today.year, today.month - month_index, 1).timestamp() * 1000
        unix_end = (datetime(today.year, today.month + 1 - month_index, 1) - timedelta(seconds=1)).timestamp() * 1000
        print(unix_start, unix_end)

        filename = f"{exchange.name}-kline-{datetime(today.year, today.month - month_index, 1).strftime('%Y-%m')}"
        path_csv = f"{tmp_path}/kline/{filename}.csv"
        path_tar = f"{tmp_path}/kline/{filename}.tar.xz"
        if os.path.exists(path_tar):
            continue

        # 下载
        exchan.load_all(timeframe=timeframe)
        # 保存
        exchan.table.to_csv(path_tar)
        # 压缩
        with tarfile.open(path_tar, "w:xz") as tar:
            tar.add(path_csv)
        # 删除
        os.remove(path_csv)
