# -*- coding: utf-8 -*-
# url fetching & parsing helper
import time
import os.path
import codecs
import urllib
import json
from BeautifulSoup import BeautifulSoup
import subprocess

import logging

import settings

# misc ---


def load_urls():
    if not os.path.isfile(settings.URLS_FILE):
        return settings.URLS_TO_FETCH
    f = codecs.open(settings.URLS_FILE, 'r', "utf-8")
    t = f.read()
    f.close()
    res = json.loads(t)
    return res


def save_urls(urls):
    f = codecs.open(settings.URLS_FILE, 'w', "utf-8")
    j = json.dumps(urls)
    f.write(j)
    f.close()


# fetching & parsing methods ---

def fetch_and_parse(url, filepath):
    """
    Fetching URL, parsing <TITLE>, saving to cache
    """
    print "fetch %s" % (url)
    page = urllib.urlopen(url).read()
    #  @todo: add gzip support

    parsed_html = BeautifulSoup(page)
    res = parsed_html.head.find('title').text

    try:
        f = codecs.open(filepath, "w", "utf-8")
        f.write(res)
        f.close()
    except:
        logging.error("Something went wrong with writing %s", filepath)
        raise

    return {"url": url, "result": res}


def check_cache_dir():
    """
    Check and create cache directory if needed
    """
    try:
        if not os.path.isdir(settings.CACHE_DIR):
            os.makedirs(settings.CACHE_DIR)
    except:
        logging.error("There is a problem with a cache directory")
        raise


def is_cache_file_expired(filepath,
                          cache_timeout=settings.DEFAULT_CACHE_TIMEOUT):
    if os.path.isfile(filepath) \
       and os.path.getsize(filepath) > 0:
        stat = os.stat(filepath)
        mod_time = stat.st_mtime
        return time.time() >= mod_time + cache_timeout
    return True


def checkout(url, filename, cache_timeout=settings.DEFAULT_CACHE_TIMEOUT,
             force=False):
    """
    Check for cache timeout, update if needed or forced
    """
    if not filename:
        return None
    check_cache_dir()
    filepath = os.path.join(settings.CACHE_DIR, filename)
    if not is_cache_file_expired(filepath, cache_timeout=cache_timeout) \
       and not force:
        f = codecs.open(filepath, 'r', "utf-8")
        res = f.read()
        f.close()
        return {"url": url, "result": res, "from_cache": True}
    return fetch_and_parse(url, filepath)


def _checkout(kwargs):
    return checkout(**kwargs)


def update(urls=settings.URLS_TO_FETCH,
           cache_timeout=settings.DEFAULT_CACHE_TIMEOUT):
    for u in urls:
        filepath = os.path.join(settings.CACHE_DIR, u['filename'])
        if is_cache_file_expired(filepath, cache_timeout=cache_timeout):
            print "cache expired"
            # fetching using multiprocess
            subprocess.call(["python", settings.FETCH_PY])
            break

    # load from cache or ... (see checkout_all() for more...)
    return checkout_all(urls=load_urls(), pool=None)


def checkout_all(urls=settings.URLS_TO_FETCH, pool=None):
    """
    Check cache (and fetch) in multiprocess mode (if pool was provided)
    """

    if pool:
        print "using pool"
        r = pool.map(_checkout, urls)
    else:
        r = [_checkout(u) for u in urls]

    return r

'''

Общая схема такова:
1. проверяем, не "протух" ли кэш (update)
2.1. если что-то "протухло", то пытаемся апдейтить все через subprocess,
    в котором задачи параллелятся
2.2. на самом деле, обновляется только "протухшее" (checkout)
3. возвращаем все из кеша
3.1. но если вдруг случилась фантастическая ситуация и на этом шаге кеша нет,
    то есть возможность загрузить недостающее на лету

'''
