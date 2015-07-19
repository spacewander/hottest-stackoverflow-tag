#!/usr/bin/env python3
# coding: utf-8

import datetime
import os
from sys import argv

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
    Data is a list of (tagname, count). We will write data into file with format below:
    tag1\t\t\tcount
    tag2\t\t\tcount
    ...
    """
    data.sort(key=lambda data:data[1], reverse=True)
    with open(
            os.path.join(os.path.dirname(
                os.path.realpath(__file__)), DATA_DIR, filename), 'w') as f:
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
    for i, tag in enumerate(new): # tag : [tagname, count]
        while j < old_len and old[j][0] < tag[0]:
            j += 1
        if j >= old_len:
            continue
        if old[j][0] == tag[0]:
            data.append((tag[0], tag[1] - old[j][1]))
            j += 1
        else:
            data.append(tag[0], tag[1] - LOWEST_SCORE)
    if output == '': # write to stdout
        for tag in data:
            if tag[1] > 0:
                print(tag_to_string(tag))
    else:
        with open(output, 'a') as f:
            for tag in data:
                if tag[1] > 0:
                    f.write(tag_to_string(tag) + '\n')


def main():
    if len(argv) == 3:
        if not (os.path.isfile(argv[1]) and os.path.isfile(argv[2])):
            raise ValueError("Given file does not exist.")
        old = argv[1]
        new = argv[2]
        extract_changed_tags(old, new)

    else:
        start_at = datetime.datetime.now()
        data = crawl_tags_using_threads(5)
        end_at = datetime.datetime.now()
        print("Time used: %d" % (end_at - start_at).total_seconds())
        if len(data) > 0:
            print("Get tags %d" % len(data))
            extract_tags_to_file(data, transform_time_to_filename(start_at))

if __name__ == '__main__' :
    main()

