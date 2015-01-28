# -*- coding: utf-8 -*-
# settings for this app
import os.path

DEFAULT_CACHE_TIMEOUT = 60*5  # 5 seconds by default

URLS_TO_FETCH = [{"url": "http://ya.ru", "filename": "yaru", },
                 {"url": "http://python.org", "filename": "pyorg",
                  "cache_timeout": 60*5},
                 {"url": "http://ru.wikipedia.org", "filename": "wikipedik"},
                 ]

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
FETCH_PY = os.path.join(os.path.dirname(__file__), "_fetch.py")
URLS_FILE = os.path.join(os.path.dirname(__file__), 'urls.json')

SECRET_KEY = '12654874303548708465403213248703532013578706543521378970651'
