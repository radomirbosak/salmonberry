from .common import load_cache, load_labels, load_ratings


def load_articles(cache_filename, labels_filename=None, ratings_filename=None):
    cache = load_cache(cache_filename)
    labels = load_labels(labels_filename) if labels_filename else []
    ratings = load_ratings(ratings_filename) if ratings_filename else []

    label_map = {a['id']: a['labels'] for a in labels}
    rating_map = {a['id']: a['rating'] for a in ratings}

    for article in cache:
        article['labels'] = label_map.get(article['id'], None)
        article['rating'] = rating_map.get(article['id'], None)

    return cache
