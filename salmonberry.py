#!/usr/bin/env python3
import logging
import argparse
from collections import Counter

import yaml
import feedparser
import scipy
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)


RATING_FILENAME = 'ratings.yaml'
FEEDS_FILENAME = 'feeds.yaml'
CACHE_FILENAME = 'cache.yaml'
LABELS_FILENAME = 'labels.yaml'


class Predictor:

    def __init__(self, entries):
        self.entries = entries

        if not self.entries:
            return

        self.vectorizer = get_vectorizer(entries)
        vectors = get_vectors(entries, self.vectorizer)

        self.transformer = TfidfTransformer()
        self.features = self.transformer.fit_transform(vectors)

        self.linreg = LinearRegression()
        self.targets = scipy.array([1 if ans['rating'] == 'y'
                                    else 0 for ans in entries])
        self.linreg.fit(self.features, self.targets)

    def predict(self, new_title):
        if not self.entries:
            return None

        new_vect = self.vectorizer.transform([new_title])
        new_vect2 = self.transformer.transform(new_vect)
        return self.linreg.predict(new_vect2)[0]

    @property
    def error(self):
        # -- 1.
        errors = []
        k_fold = 10

        for _ in range(k_fold):
            train_feat, test_feat, train_tar, test_tar = \
                train_test_split(self.features, self.targets)

            test_lin_reg = LinearRegression()
            test_lin_reg.fit(train_feat, train_tar)

            test_pred = test_lin_reg.predict(test_feat)

            absvals = np.abs(test_tar - test_pred)
            errors.append(absvals.mean())

        return np.average(errors), np.std(errors)


def percent(value):
    return int(round(value * 100))


def get_vectorizer(entries):
    titles = [doc["title"] for doc in entries]
    vect = CountVectorizer()
    vect.fit(titles)
    return vect


def get_vectors(entries, vectorizer):
    titles = [doc["title"] for doc in entries]
    return vectorizer.transform(titles)


def get_feed_urls(filename):
    with open(FEEDS_FILENAME) as fd:
        return yaml.load(fd)


def get_all_entries(feed_urls):
    entries = []

    for url in feed_urls:
        feed = feedparser.parse(url)
        entries += to_dicts(feed.entries)

    logging.debug('Downloaded %d entries from %d feeds.', len(entries), len(feed_urls))

    return entries


def save_ratings(answers, filename):
    with open(filename, 'w') as fd:
        yaml.dump(answers, fd)


def load_ratings(filename):
    try:
        with open(filename, 'r') as fd:
            return yaml.load(fd)
    except FileNotFoundError:
        return {}


def learn():
    urls = get_feed_urls(FEEDS_FILENAME)
    fetched_entries = get_all_entries(urls)

    answers = load_ratings(RATING_FILENAME)

    predictor = Predictor(answers.values())

    new_entries = {entry for entry in fetched_entries if entry.link not in answers}
    print(f'Found {len(new_entries)} new entries, {len(answers)} old entries.')

    new_answers = {}
    print('Are these titles interesting? [y/n]')
    for i, entry in enumerate(new_entries, start=1):

        prompt = f'{i}/{len(new_entries)} | {entry.title}: [y/n] '

        value = predictor.predict(entry.title)
        if value is not None:
            print(f'Predicted value: {percent(value)}%')

        try:
            answer = input(prompt)
        except EOFError:
            print()
            logging.debug('Exiting')
            break

        entrydict = dict(entry)
        entrydict['rating'] = answer

        new_answers[entry.link] = entrydict

    c = Counter([ans['rating'] for ans in new_answers.values()])

    others = len(new_answers) - c["y"] - c["n"]
    print(f'Answers | yes: {c["y"]}, no: {c["n"]}, others: {others}')

    answers.update(new_answers)
    save_ratings(answers, RATING_FILENAME)


def to_dicts(tree):
    if isinstance(tree, feedparser.FeedParserDict):
        return {key: to_dicts(value) for key, value in tree.items()}
    elif isinstance(tree, list):
        return [to_dicts(el) for el in tree]
    else:
        return tree


def load_yaml(filename, default=[]):
    try:
        with open(filename, 'r') as fd:
            return yaml.load(fd) or default
    except FileNotFoundError:
        return default


def save_yaml(data, filename):
    with open(filename, 'w') as fd:
        yaml.dump(data, fd)


def load_cache(cache_filename):
    cache = load_yaml(cache_filename, default=[])
    logging.debug('Loaded %d old entries.', len(cache))
    return cache


def update_cache(old_cache, new_entries):
    old_ids = {entry['id'] for entry in old_cache}
    num_new = 0
    for entry in new_entries:
        if entry['id'] not in old_ids:
            old_cache.append(entry)
            old_ids.add(entry['id'])
            num_new += 1

    logging.debug('Added %d new entries to cache.', num_new)


def save_cache(data, cache_filename):
    save_yaml(data, cache_filename)


def load_labels(labels_filename):
    labels = load_yaml(labels_filename)
    logging.debug('Loaded %d labels.', len(labels))
    return labels


def save_labels(data, labels_filename):
    save_yaml(data, labels_filename)


def get_unlabeled(cache, labels):
    labeled_ids = set(entry['id'] for entry in labels)
    return [entry for entry in cache if entry['id'] not in labeled_ids]


def ask_labels(entry):
    print('Title: ' + entry['title'])
    answer = input('Labels: ')
    return answer.split()

def download(feeds_filename, cache_filename):
    feed_urls = get_feed_urls(feeds_filename)
    fetched_entries = get_all_entries(feed_urls)

    cache = load_cache(cache_filename)
    update_cache(cache, fetched_entries)
    save_cache(cache, cache_filename)
    print('Cache updated.')


def label(cache_filename, labels_filename):
    # load cache
    cache = load_cache(cache_filename)
    labeled = load_labels(labels_filename)

    # get unlabeled entries
    unlabeled = get_unlabeled(cache, labeled)

    # ask for label(s)
    print('For each article enter space-separated list of labels.')
    num_new_labels = 0
    try:
        for entry in unlabeled:
            labels = ask_labels(entry)
            labeled.append({'id': entry['id'], 'labels': labels})
            num_new_labels += 1
    except EOFError:
        logging.debug('Labeling interrupted')

    # write down labels
    logging.debug('Writing %d labels', num_new_labels)
    save_labels(labeled, labels_filename)


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

    return parser.parse_args()


def main():
    args = parse_args()

    if args.action == 'download':
        download(args.feed_list, args.cache)
    elif args.action == 'label':
        label(args.cache, args.labels)


if __name__ == '__main__':
    main()
