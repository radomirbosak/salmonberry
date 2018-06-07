import logging

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

from .common import load_cache, load_yaml, save_yaml, load_labels, load_ratings
from .article import load_articles


def ask_rating():
    while True:
        answer = input('Rating x/z: ')
        if answer not in ['x', 'z']:
            print('Only values "x" and "z" are allowed.')
            continue

        return answer


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
            answer = ask_rating()
            ratings.append({
                'id': article['id'],
                'rating': answer,
            })
    except EOFError:
        logging.debug('Rating interrupted.')

    # 5. save ratings
    save_yaml(ratings, ratings_filename)


def predict_rating(cache_filename, labels_filename, ratings_filename):
    # 1. load article cache, labels, and ratings
    # cache = load_cache(cache_filename)
    # labeled = load_labels(labels_filename)
    # labels_map = {article['id']: article['labels'] for article in labeled}
    # ratings = load_ratings(ratings_filename)

    articles = load_articles(cache_filename, labels_filename, ratings_filename)
    rated = [a for a in articles if a['rating'] is not None]

    # get xs
    logging.debug('preparing xs')
    titles = [a['title'] for a in rated]
    vectorizer = TfidfVectorizer(max_features=1000)
    xs = vectorizer.fit_transform(titles)

    # get ys
    ys = np.array([a['rating'] == 'x' for a in rated], dtype=np.int)

    # train model
    classifier = LogisticRegression(C=10)
    classifier.fit(xs, ys)

    # fetch sentence
    sentence = input('Sentence: ')

    # predict
    features = vectorizer.transform([sentence])
    rating = classifier.predict_proba(features)[0][1]

    # display result
    print('Predicted rating: {:5.2f}%'.format(100 * rating))
