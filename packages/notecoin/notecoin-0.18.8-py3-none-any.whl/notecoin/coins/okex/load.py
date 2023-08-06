import os

import ccxt
from notecoin.coins.base.cron import load_month
from notefile.compress import tarfile

path_root = '/home/bingtao/workspace/tmp/notecoin/'

# with tarfile.open(path_tar, "w:xz") as tar:
#     tar.add(path_csv)
load_month(ccxt.okex(),tmp_path=path_root)
