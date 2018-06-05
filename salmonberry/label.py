import logging

from .common import load_yaml, save_yaml, load_cache

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
