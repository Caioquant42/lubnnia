#!/usr/bin/env python3

import sys
import os
# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)
from backend.apps.utils.dict import TICKERS_DICT

from datetime import datetime, timedelta
import requests
import csv
import dolphindb as ddb
import pandas as pd

import time
from datetime import datetime, timedelta
import subprocess

# Create a session and connect to the DolphinDB server
s = ddb.session()
s.connect("46.202.149.154", 8848, "admin", "123456")