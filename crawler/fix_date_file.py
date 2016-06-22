#!/usr/bin/env python
# coding: utf-8
"""Fix date file yy-mm-dd with nearest file in two side.
For example, assumed we have `16-01-01` and `16-01-04`,
need to fix `16-01-02` and `16-01-03`:
    16-01-01                16-01-04
    a 200                   a 240
    b 100                   b 112
    c 8                     d 9

After running this script, there will be two new file:
    16-01-02-fix            16-01-03-fix
    a 213                   a 226
    b 104                   b 108

c and d will be ignored, since their counts may just over the limit.
As a result, *-fix will be shorter than its nearest files.
"""
import datetime
import os
import re
import sys
from config import META_DATA_LINES


def to_date(fn):
    year = 2000 + int(fn[:2])
    month = int(fn[3:5])
    day = int(fn[6:8])
    return datetime.date(year, month, day)

def next_date(start_date, end_date):
    "Return a generator which returns dates in [start_date, end_date]"
    delta = datetime.timedelta(1)
    while start_date <= end_date:
        yield start_date
        start_date += delta


def get_tags_from_file(fn):
    "Return [(tagname, count), ...]"
    with open(fn) as f:
        for i in range(META_DATA_LINES):
            next(f)
        tags = []
        for line in f:
            tagname, count = line.split()
            tags.append((tagname, int(count)))
        return tags

def filter_common_tags(tags_a, tags_b):
    """Given tags_a: [(a, 3), (b, 1), (d, 1)], tags_b: [(a, 2), (b, 2), (c, 1)],
    Return [(a, 3, 2), (b, 1, 2)]. Assume both tags are sorted by count.
    """
    tags = tags_a + tags_b
    tagnames = {}
    for tag in tags:
        name, count = tag
        if name not in tagnames:
            tagnames[name] = [count]
        else:
            tagnames[name].append(count)
    result = []
    for tag, counts in tagnames.items():
        if len(counts) == 2:
            result.append((tag, counts[0], counts[1]))
    return result

def extract_tags_to_file(data, filename):
    """Data is a list of (tagname, count).
    We will write data into file with format below:
    tag1\t\t\tcount
    tag2\t\t\tcount
    """
    data.sort(key=lambda tag: tag[1], reverse=True)
    with open(filename, 'w') as f:
        # first four lines for metadata
        f.write(filename + '\n')
        f.write('tags: %d\n\n\n' % len(data))
        for tag in data:
            f.write('%s\t\t\t%d\n' % (tag[0], tag[1]))

def fix(to_fix_dates, beginning_file, end_file, dest):
    tags_a = get_tags_from_file(beginning_file)
    tags_b = get_tags_from_file(end_file)
    common_tags = filter_common_tags(tags_a, tags_b)
    dist = len(to_fix_dates) + 1
    for i, date in enumerate(to_fix_dates):
        fn = date.isoformat()[2:] + '-fix'
        print("%s with %s and %s" % (fn, beginning_file, end_file))
        fn = os.path.join(dest, fn)
        tags = []
        for tag in common_tags:
            name, beginning_value, end_value = tag
            diff = end_value - beginning_value
            tags.append((name, int(beginning_value + diff / dist * (i+1))))
        extract_tags_to_file(tags, fn)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s data_file_dir' % sys.argv[0])
        sys.exit(1)
    dest_dir = sys.argv[1]
    pattern = re.compile(r'\d\d-\d\d-\d\d.*')
    files = filter(lambda fn: re.match(pattern, fn), os.listdir(dest_dir))
    files.sort() # lexicographical order is enough
    start_date = to_date(files[0])
    end_date = to_date(files[-1])
    date_to_file = {}
    for fn in files:
        date_to_file[to_date(fn)] = os.path.join(dest_dir, fn)

    beginning_file = date_to_file[start_date]
    to_fix_dates = []
    for date in next_date(start_date, end_date):
        if date in date_to_file:
            if len(to_fix_dates) > 0:
                fix(to_fix_dates, beginning_file, date_to_file[date], dest_dir)
                to_fix_dates = []
            beginning_file = date_to_file[date]
        else:
            to_fix_dates.append(date)
