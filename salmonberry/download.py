import yaml
import logging

import feedparser

from .common import load_cache, update_cache, save_cache


def get_feed_urls(filename):
    with open(filename) as fd:
        return yaml.load(fd)


def get_all_entries(feed_urls):
    entries = []

    for url in feed_urls:
        feed = feedparser.parse(url)
        entries += to_dicts(feed.entries)

    logging.debug('Downloaded %d entries from %d feeds.', len(entries), len(feed_urls))

    return entries


def to_dicts(tree):
    if isinstance(tree, feedparser.FeedParserDict):
        return {key: to_dicts(value) for key, value in tree.items()}
    elif isinstance(tree, list):
        return [to_dicts(el) for el in tree]
    else:
        return tree


def download(feeds_filename, cache_filename):
    feed_urls = get_feed_urls(feeds_filename)
    fetched_entries = get_all_entries(feed_urls)

    cache = load_cache(cache_filename)
    update_cache(cache, fetched_entries)
    save_cache(cache, cache_filename)
    print('Cache updated.')
