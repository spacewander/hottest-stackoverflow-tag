#!/usr/bin/env python
# coding: utf-8
from sys import argv, exit
import os

from main import DATA_DIR

# The lines of metadata in tag files
META_DATA_LINES = 4

def get_first_N_tags(tag_file, N):
    with open(tag_file) as f:
        tags = [line.split() for line in f][META_DATA_LINES:]
        # no need to sort tags, the tags have been sorted with count yet
        for tag_rank, tag in enumerate(tags):
            print tag[0]
            if tag_rank == N:
                return

def get_first_N_languages(tag_file, N, languages):
    with open(tag_file) as f:
        tags = [line.split() for line in f][META_DATA_LINES:]
        language_rank = 0
        for tag in tags:
            name = tag[0]
            if name in languages:
                print name
                language_rank += 1
            if language_rank == N:
                return


def get_rank_of_language(tag_file, language, languages):
    with open(tag_file) as f:
        tags = [line.split() for line in f][META_DATA_LINES:]
        # no need to sort tags, the tags have been sorted with count yet
        language_rank = 0
        for tag_rank, tag in enumerate(tags):
            name = tag[0]
            if name in languages:
                language_rank += 1
            if name == language:
                print "The tag rank is %d" % (tag_rank + 1)
                print "The language rank is %d" % language_rank
                return
    print 'Tag not found'

def get_rank_of_tag(tag_file, tag_name):
    with open(tag_file) as f:
        tags = [line.split() for line in f][META_DATA_LINES:]
        for tag_rank, tag in enumerate(tags):
            name = tag[0]
            if name == tag_name:
                print "The tag rank is %d" % (tag_rank + 1)
                return
    print 'Tag not found'

def print_usage(script_name):
    print "Usage: %s [tagname| -t tag_rank | -l language" % script_name
    print "Print the tag rank (and language rank) of given target"

def main():
    if len(argv) not in (2, 3) or (len(argv) == 3 and argv[1] not in ('-t', '-l')):
        print_usage(argv[0])
        exit(1)

    with open('languages.txt') as f:
        languages = frozenset([language.strip() for language in f])

    # the files list is sorted by created time
    latest_tag_file = sorted(
            os.listdir(os.path.join('.', DATA_DIR)), reverse=True)[0]
    latest_tag_file = os.path.join('.', DATA_DIR, latest_tag_file)
    if len(argv) == 3:
        if argv[1] == '-t':
            get_first_N_tags(latest_tag_file, int(argv[2]))
        elif argv[1] == '-l':
            get_first_N_languages(latest_tag_file, int(argv[2]), languages)
    else:
        target = argv[1]
        if target in languages:
            get_rank_of_language(latest_tag_file, target, languages)
        else:
            get_rank_of_tag(latest_tag_file, target)

if __name__ == '__main__':
    main()
