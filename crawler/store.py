#!/usr/bin/env python
# coding: utf-8

import os
import re
import sys
import redis

Redis = redis.StrictRedis(host='localhost', port=6379, db=0)
# date:yymmdd is zset{language: number}
# language:xx is zset{'date:number': date}. For example, '160101:2000': 160101.


def store_date_file(fn):
    # filename should be `yy-mm-dd...`
    prefix = ''.join(os.path.basename(fn).split('-')[:3])
    date_key = 'date:' + prefix
    languages = []
    with open(fn) as f:
        for i in range(4):
            next(f)
        pipe = Redis.pipeline()
        for line in f:
            name, value = line.split()
            languages.append(value)
            languages.append(name)
            pipe.zadd('language:' + name,
                      int(prefix), prefix + ':' + str(value))
        pipe.zadd(date_key, *languages)
        pipe.execute()


def get_stored_dates():
    prefix = 'date:'
    prefix_end = len(prefix)
    return set(date[prefix_end:] for date in Redis.keys(prefix + '*'))


def get_date_files(dirname):
    date_files = {}
    pattern = re.compile('^\d\d-\d\d-\d\d-\d\d-\d\d$')
    for fn in os.listdir(dirname):
        if re.match(pattern, fn) is None:
            continue
        # filename should be `yy-mm-dd...`
        date_files[fn[:8]] = os.path.join(dirname, fn)
    return date_files


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s filename/dirname.' % sys.argv[0])
        print('If `filename` is given, store the data of file into redis.')
        print('Otherwise store data from each file under gien directory.')
        sys.exit(1)
    if os.path.isfile(sys.argv[1]):
        store_date_file(sys.argv[1])
    else:
        date_files = get_date_files(sys.argv[1])
        to_store_dates = set(date_files.keys()) - get_stored_dates()
        for date in to_store_dates:
            print('Storing data ' + date)
            store_date_file(date_files[date])
