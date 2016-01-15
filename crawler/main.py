#!/usr/bin/env python
# coding: utf-8

import logging
import os
import sys
from datetime import datetime
from os.path import dirname, isdir, isfile, join, realpath

from crawler import crawl_tags_using_threads, LOWEST_SCORE

DATA_DIR = 'data'


def transform_time_to_filename(time):
    """
    Transform Datetime into filename, with format 'yy-mm-dd-HH-MM'
    """
    return time.strftime('%y-%m-%d-%H-%M')


def tag_to_string(tag):
    """
    convert tag into string
    """
    return "%s\t\t\t%d" % (tag[0], tag[1])


def extract_tags_to_file(data, filename):
    """
    Data is a list of (tagname, count).
    We will write data into file with format below:
    tag1\t\t\tcount
    tag2\t\t\tcount
    ...
    """
    data.sort(key=lambda data: data[1], reverse=True)
    with open(
            join(dirname(realpath(__file__)), DATA_DIR, filename), 'w') as f:
        # first four lines for metadata
        f.write(filename + '\n')
        f.write('tags: %d\n' % len(data))
        f.write('\n\n')
        for tag in data:
            f.write(tag_to_string(tag) + '\n')


def extract_changed_tags(old, new, output=''):
    """
    Extract the changed tags between two tags files.
    If output not given, write the result to stdout.
    """
    def tag_to_tuple(tag):
        name, count = tag.split()
        return (name, int(count))

    # first four lines for metadata
    with open(new) as f:
        new = [tag_to_tuple(tag) for tag in f][4:]
    with open(old) as f:
        old = [tag_to_tuple(tag) for tag in f][4:]

    new.sort(key=lambda tag: tag[0])
    old.sort(key=lambda tag: tag[0])
    # The result in tag file is sorted by name
    old_len = len(old)
    j = 0
    data = []
    # Ignore the case that tags in old file is not existed in new one.
    for i, tag in enumerate(new):  # tag : [tagname, count]
        while j < old_len and old[j][0] < tag[0]:
            j += 1
        if j >= old_len:
            continue
        if old[j][0] == tag[0]:
            data.append((tag[0], tag[1] - old[j][1]))
            j += 1
        else:
            data.append(tag[0], tag[1] - LOWEST_SCORE)
    if output == '':  # write to stdout
        for tag in data:
            if tag[1] > 0:
                print(tag_to_string(tag))
    else:
        with open(output, 'a') as f:
            for tag in data:
                if tag[1] > 0:
                    f.write(tag_to_string(tag) + '\n')


def create_logger(with_file=True):
    logger = logging.getLogger(__name__.split('.')[0])
    # show all level of logs
    logger.setLevel(getattr(logging, 'DEBUG'))
    FORMAT = '[%(levelname)s] %(threadName)s %(asctime)s %(message)s'
    DATE_FORMAT = '%H:%M:%S'
    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
    if with_file:
        log_dir = join(dirname(realpath(__file__)), 'log')
        if not isdir(log_dir):
            os.mkdir(log_dir)
        now = datetime.now()
        log_file = join(log_dir, transform_time_to_filename(now))
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_today_data_filename():
    now = datetime.now()
    today_data_file_prefix = transform_time_to_filename(now)[:8]  # yy-mm-dd
    data_dir = join(dirname(realpath(__file__)), DATA_DIR)
    files = os.listdir(data_dir)
    for fn in files:
        if fn.startswith(today_data_file_prefix):
            return fn
    return None


def main():
    if len(sys.argv) == 3:
        if not (isfile(sys.argv[1]) and isfile(sys.argv[2])):
            raise ValueError("Given file does not exist.")
        old = sys.argv[1]
        new = sys.argv[2]
        extract_changed_tags(old, new)

    else:
        data_dir = join(dirname(realpath(__file__)), DATA_DIR)
        if not isdir(data_dir):
            os.mkdir(data_dir)

        force_crawling = False
        if not force_crawling:
            data_file = get_today_data_filename()
            if data_file is not None:
                print("Today's crawling is done. Data file %s is found."
                      % data_file)
                return

        logger = create_logger(with_file=True)
        # logger = create_logger()
        start_at = datetime.now()
        data = crawl_tags_using_threads(5, logger)
        end_at = datetime.now()
        logger.info("Time used: %d" % (end_at - start_at).total_seconds())
        if len(data) > 0:
            logger.info("Get tags %d" % len(data))
            extract_tags_to_file(data, transform_time_to_filename(start_at))

if __name__ == '__main__':
    main()
