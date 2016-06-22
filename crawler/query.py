#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple
from sys import argv, exit
import os

from config import DATA_DIR, META_DATA_LINES

Tag = namedtuple('Tag', ['name', 'value'])


def extract_tag_from(line):
    name, value = line.split()
    return Tag(name, int(value))


def get_tags_from_file(fn):
    """Return an unorder dict of Tags"""
    with open(fn) as f:
        tags = {}
        for line_num, line in enumerate(f):
            if line_num >= META_DATA_LINES:
                tag = extract_tag_from(line)
                tags[tag.name] = tag.value
        return tags


def diff_from_tag_files(old_file, new_file):
    """
    Return an order list contains the difference of tags
    in either old_file or new_file.
    For example:
        old file:
        x 20000
        y 10000

        new file:
        x 30000
        z 10000

        Then the temp file:
        x 10000
        z 10000
    """
    old_tags = get_tags_from_file(old_file)
    new_tags = get_tags_from_file(new_file)
    tags = []
    for tag in new_tags:
        if tag in old_tags:
            tags.append(Tag(tag, new_tags[tag] - old_tags[tag]))
        else:
            tags.append(Tag(tag, new_tags[tag]))
    return sorted(tags, key=lambda x: -x.value)


def get_first_N_tags(old_file, new_file, N):
    diff = diff_from_tag_files(old_file, new_file)
    for tag_rank, tag in enumerate(diff):
        print("%d\t%s" % (tag_rank + 1, tag.name))
        if tag_rank == N:
            return


def get_first_N_languages(old_file, new_file, N, languages):
    diff = diff_from_tag_files(old_file, new_file)
    language_rank = 0
    for tag in diff:
        if tag.name in languages:
            print("%d\t%s" % (language_rank + 1, tag.name))
            language_rank += 1
        if language_rank == N:
            return


def get_rank_of_language(old_file, new_file, language, languages):
    diff = diff_from_tag_files(old_file, new_file)
    language_rank = 0
    for tag_rank, tag in enumerate(diff):
        name = tag.name
        if name in languages:
            language_rank += 1
        if name == language:
            print("The tag rank is %d" % (tag_rank + 1))
            print("The language rank is %d" % language_rank)
            print("The tag number is %d" % tag.value)
            return
    print('Tag not found')


def get_rank_of_tag(old_file, new_file, tag_name):
    diff = diff_from_tag_files(old_file, new_file)
    for tag_rank, tag in enumerate(diff):
        name = tag.name
        if name == tag_name:
            print("The tag rank is %d" % (tag_rank + 1))
            print("%d tags created in the period" % tag.value)
            return
    print('Tag not found')


def print_usage(script_name):
    print("Usage: %s [tagname| -t tag_rank | -l language" % script_name)
    print("Print the tag rank (and language rank) of given target")


def filter_data_file(fn):
    return len(fn) == 14  # yy-MM-dd-hh-mm


def convert_filename_to_timestamp(fn):
    """convert filename yy-MM-dd-hh-mm to timestamp yy-MM-dd hh:mm"""
    parts = fn.split('-')
    if len(parts) != 5:
        raise ValueError("filename should be in yy-MM-dd-hh-mm format")
    return "%s-%s-%s %s:%s" % (
        '20' + parts[0][-2:], parts[1], parts[2], parts[3], parts[4])


def main():
    if len(argv) not in (2, 3) or (
            len(argv) == 3 and argv[1] not in ('-t', '-l')):
        print_usage(argv[0])
        exit(1)

    with open('languages.txt') as f:
        languages = frozenset([language.strip() for language in f])

    data_dir = os.path.join('.', DATA_DIR)
    # the files list is sorted by created time
    latest_tag_file = sorted(filter(filter_data_file, os.listdir(data_dir)),
                             reverse=True)[0]
    latest_tag_file = os.path.join(data_dir, latest_tag_file)
    oldest_tag_file = sorted(filter(filter_data_file, os.listdir(data_dir)))[0]
    oldest_tag_file = os.path.join(data_dir, oldest_tag_file)

    print("From %s to %s" % (
        convert_filename_to_timestamp(oldest_tag_file),
        convert_filename_to_timestamp(latest_tag_file)))

    # -t tagname or -l language
    if len(argv) == 3:
        if argv[1] == '-t':
            get_first_N_tags(oldest_tag_file, latest_tag_file, int(argv[2]))
        elif argv[1] == '-l':
            get_first_N_languages(oldest_tag_file, latest_tag_file,
                                  int(argv[2]), languages)
    else:
    # get tag value, tag rank and language rank, ...
        target = argv[1]
        if target in languages:
            get_rank_of_language(oldest_tag_file, latest_tag_file,
                                 target, languages)
        else:
            get_rank_of_tag(oldest_tag_file, latest_tag_file, target)

if __name__ == '__main__':
    main()
