import yaml
import logging


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
