import logging

from .common import load_cache, load_yaml, save_yaml
from .label import load_labels


def load_ratings(ratings_filename):
    ratings = load_yaml(ratings_filename)
    logging.debug('Loaded %d ratings.', len(ratings))
    return ratings


def rate(cache_filename, labels_filename, ratings_filename):
    # 1. load article cache, labels, and ratings
    cache = load_cache(cache_filename)
    labeled = load_labels(labels_filename)
    labels_map = {article['id']: article['labels'] for article in labeled}
    ratings = load_ratings(ratings_filename)

    # 2. take labeled unrated articles
    labeled_ids = set(a['id'] for a in labeled)
    rated_ids = set(a['id'] for a in ratings)
    articles = [a for a in cache if a['id'] in labeled_ids.difference(rated_ids)]

    if not articles:
        logging.debug('Found no new labeled unrated articles.')
        return
    logging.debug('Found %d labeled unrated articles.', len(articles))

    # 3. For each article, display the title and ask for rating
    print('Rate the following articles: x - good; z - bad.')
    try:
        for article in articles:
            labels = labels_map[article['id']]
            print('Title: ' + article['title'])
            print('Labels: ' + ', '.join(labels))
            answer = input('Rating x/z: ')
            ratings.append({
                'id': article['id'],
                'rating': answer,
            })
    except EOFError:
        logging.debug('Rating interrupted.')

    # 5. save ratings
    save_yaml(ratings, ratings_filename)
