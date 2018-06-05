import logging

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

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


def predict_labels(cache_filename, labels_filename):

    # load files
    cache = load_cache(cache_filename)
    labeled = load_labels(labels_filename)
    cache_id_map = {article['id']: article for article in cache}

    # find all labels
    all_labels = set()
    for article in labeled:
        all_labels.update(article['labels'])
    all_labels = sorted(all_labels)
    logging.debug('Found these labels: %s', ', '.join(all_labels))

    # 1. learn models from labeled articles
    # 1.1 prepare x-s
    logging.debug('preparing xs')
    titles = []
    for labeled_article in labeled:
        article = cache_id_map[labeled_article['id']]
        titles.append(article['title'])

    vectorizer = TfidfVectorizer(max_features=1000)
    xs = vectorizer.fit_transform(titles)

    # 1.2 prepare y-s for each label
    logging.debug('training classifiers')
    models = {}
    scores = []
    for label in all_labels:
        ys = [label in labeled_article['labels'] for labeled_article in labeled]
        ys = np.array(ys, dtype=np.int)

        classifier = LogisticRegression(C=10)
        classifier.fit(xs, ys)
        scores.append(classifier.score(xs, ys))
        models[label] = classifier

    logging.debug('score: %.2f +- %.2f', np.average(scores), np.std(scores))

    # 2. get user input
    sentence = input('Sentence: ')

    # 3. tokenize it and predict its labels
    features = vectorizer.transform([sentence])
    probs = []
    for label in all_labels:
        probs.append(
            (label, models[label].predict_proba(features)[0][1])
        )

    probs.sort(key=lambda x: x[1], reverse=True)
    colwidth = max(len(label) for label in all_labels)
    for label, pred in probs:
        print('{:>{colwidth}}: {:5.2f}'.format(label, 100 * pred, colwidth=colwidth))
