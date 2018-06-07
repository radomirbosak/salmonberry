#!/usr/bin/env python3
import logging
import argparse

from .download import download
from .label import label, predict_labels
from .rate import rate, predict_rating
from .stats import stats

logging.basicConfig(level=logging.DEBUG)


RATING_FILENAME = 'data/ratings.yaml'
FEEDS_FILENAME = 'data/feeds.yaml'
CACHE_FILENAME = 'data/cache.yaml'
LABELS_FILENAME = 'data/labels.yaml'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--feed-list', default=FEEDS_FILENAME)
    parser.add_argument('-c', '--cache', default=CACHE_FILENAME)
    parser.add_argument('-l', '--labels', default=LABELS_FILENAME)
    parser.add_argument('-r', '--rating', default=RATING_FILENAME)

    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    subp_down = subparsers.add_parser(
        'download',
        help='Download articles from feed.')

    subp_label = subparsers.add_parser(
        'label',
        help='Manually label unlabeled articles.')

    subp_predict_labels = subparsers.add_parser(
        'predict_labels',
        help='Autolabel given sentence.')

    subp_rate = subparsers.add_parser(
        'rate',
        help='Manually rate articles.')

    subp_predict_rating = subparsers.add_parser(
        'predict_rating',
        help='Predict rating for given sentence.')

    subp_stats = subparsers.add_parser('stats', help='Display useful statistics.')

    return parser.parse_args()


def main():
    args = parse_args()

    if args.action == 'download':
        download(args.feed_list, args.cache)
    elif args.action == 'label':
        label(args.cache, args.labels)
    elif args.action == 'predict_labels':
        predict_labels(args.cache, args.labels)
    elif args.action == 'rate':
        rate(args.cache, args.labels, args.rating)
    elif args.action == 'predict_rating':
        predict_rating(args.cache, args.labels, args.rating)
    elif args.action == 'stats':
        stats(args.cache, args.labels, args.rating)

if __name__ == '__main__':
    main()
