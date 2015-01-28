from multiprocessing import Pool
from fetch import checkout_all, load_urls

if __name__ == '__main__':
    _pool = Pool(processes=4)
    print "loading with pool"
    urls = load_urls()
    r = checkout_all(urls=urls, pool=_pool)
    _pool.close()
