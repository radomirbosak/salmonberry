import logging
from collections import Counter

import yaml
import feedparser
import scipy
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LinearRegression

logging.basicConfig(level=logging.DEBUG)


RATING_FILENAME = 'ratings.yaml'
FEEDS_FILENAME = 'feeds.yaml'


class Predictor:

    def __init__(self, entries):
        self.entries = entries

        if not self.entries:
            return

        self.vectorizer = get_vectorizer(entries)
        vectors = get_vectors(entries, self.vectorizer)

        self.transformer = TfidfTransformer()
        features = self.transformer.fit_transform(vectors)

        self.linreg = LinearRegression()
        targets = scipy.array([1 if ans['rating'] == 'y' else 0 for ans in entries])
        self.linreg.fit(features, targets)

    def predict(self, new_title):
        if not self.entries:
            return None

        new_vect = self.vectorizer.transform([new_title])
        new_vect2 = self.transformer.transform(new_vect)
        return self.linreg.predict(new_vect2)[0]


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
        entries += feed.entries

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


def main():
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


if __name__ == '__main__':
    main()
