import time

from .article import load_articles


def stats(cache_filename, labels_filename, ratings_filename):
    articles = load_articles(cache_filename, labels_filename, ratings_filename)

    num_total = len(articles)
    num_labeled = sum(1 for a in articles if a['labels'] is not None)
    num_rated = sum(1 for a in articles if a['rating'] is not None)

    print('Total articles: {}'.format(num_total))
    print('Labeled: {}'.format(num_labeled))
    print('Unlabeled: {}'.format(num_total - num_labeled))
    print('Rated: {}'.format(num_rated))
    print('Unrated: {}'.format(num_total - num_rated))
