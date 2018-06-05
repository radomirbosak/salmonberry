#!/usr/bin/env python3
import logging
import argparse
from collections import Counter

import yaml
import scipy
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from .download import download
from .label import label, predict_labels

logging.basicConfig(level=logging.DEBUG)


RATING_FILENAME = 'data/ratings.yaml'
FEEDS_FILENAME = 'data/feeds.yaml'
CACHE_FILENAME = 'data/cache.yaml'
LABELS_FILENAME = 'data/labels.yaml'


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    subp_down = subparsers.add_parser('download')
    subp_down.add_argument('-f', '--feed-list', default=FEEDS_FILENAME)
    subp_down.add_argument('-c', '--cache', default=CACHE_FILENAME)

    subp_label = subparsers.add_parser('label')
    subp_label.add_argument('-c', '--cache', default=CACHE_FILENAME)
    subp_label.add_argument('-l', '--labels', default=LABELS_FILENAME)

    subp_predict_labels = subparsers.add_parser('predict_labels')
    subp_predict_labels.add_argument('-c', '--cache', default=CACHE_FILENAME)
    subp_predict_labels.add_argument('-l', '--labels', default=LABELS_FILENAME)

    return parser.parse_args()


def main():
    args = parse_args()

    if args.action == 'download':
        download(args.feed_list, args.cache)
    elif args.action == 'label':
        label(args.cache, args.labels)
    elif args.action == 'predict_labels':
        predict_labels(args.cache, args.labels)


if __name__ == '__main__':
    main()
