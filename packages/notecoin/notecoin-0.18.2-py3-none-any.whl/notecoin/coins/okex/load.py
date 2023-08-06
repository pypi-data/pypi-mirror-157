import os
import tarfile
import zipfile

import ccxt
from notecoin.coins.base.cron import load_month
from notecoin.coins.base.load import LoadDataKline
from notefile.compress import tarfile
from tqdm import tqdm

path_root = '/home/bingtao/workspace/tmp/notecoin/'
# path_csv = f'{path_root}/data.csv'
# path_tar = f'{path_root}/data.tar.xz'

# with tarfile.open(path_tar, "w:xz") as tar:
#     tar.add(path_csv)
load_month(ccxt.okex(),tmp_path=path_root)
