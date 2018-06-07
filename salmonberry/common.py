import yaml
import logging


def load_yaml(filename, default=list):
    if default is list:
        default = list()

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


def load_ratings(ratings_filename):
    ratings = load_yaml(ratings_filename)
    logging.debug('Loaded %d ratings.', len(ratings))
    return ratings
