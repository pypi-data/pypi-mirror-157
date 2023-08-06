import logging
import os

from ccxt import Exchange, okex
from notecoin.coins.base.load import LoadDataKline
from notecoin.utils.time import day_during, month_during, week_during
from notefile.compress import tarfile

logger = logging.getLogger()


def load_and_save(exchange: Exchange, tmp_path, start_datetime, end_datetime, timeframe='1m', file_format='%Y-%m'):
    exchan = LoadDataKline(exchange)
    unix_start = int(start_datetime.timestamp() * 1000)
    unix_end = int(end_datetime.timestamp() * 1000)
    print(unix_start, unix_end)
    filename = f"{exchange.name.lower()}-kline-{timeframe}-{start_datetime.strftime(file_format)}"
    path_csv = f"{tmp_path}/kline/{filename}.csv"
    path_tar = f"{tmp_path}/kline/{filename}.tar.xz"
    if os.path.exists(path_tar):
        logger.info("file exists.")
        return
    # 下载
    exchan.load_all(timeframe=timeframe, unix_start=unix_start, unix_end=unix_end)
    # 保存
    exchan.table.to_csv_all(path_csv, page_size=1000000)
    # 压缩
    with tarfile.open(path_tar, "w:xz") as tar:
        tar.add(path_csv)
    # 删除
    os.remove(path_csv)
    exchan.table.delete_all()


def load_monthly(exchange: Exchange, tmp_path, timeframe='1m'):
    for index in range(1, 10):
        start_datetime, end_datetime = month_during(index)
        load_and_save(exchange, tmp_path, start_datetime, end_datetime, timeframe, file_format='%Y-%m')


def load_weekly(exchange: Exchange, tmp_path, timeframe='1m'):
    for index in range(1, 10):
        start_datetime, end_datetime = week_during(index)
        load_and_save(exchange, tmp_path, start_datetime, end_datetime, timeframe, file_format='%Y-%m-%d')


def load_daily(exchange: Exchange, tmp_path, timeframe='1m'):
    for index in range(1, 10):
        start_datetime, end_datetime = day_during(index)
        load_and_save(exchange, tmp_path, start_datetime, end_datetime, timeframe, file_format='%Y-%m-%d')


path_root = '/home/bingtao/workspace/tmp/notecoin'

load_weekly(okex(), tmp_path=path_root)
