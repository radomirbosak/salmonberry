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


def get_feed_urls(filename):
    with open(FEEDS_FILENAME) as fd:
        return yaml.load(fd)


def get_all_entries(feed_urls):
    entries = []

    for url in feed_urls:
        feed = feedparser.parse(url)
        entries += feed.entries

    return entries


def main():
    urls = get_feed_urls(FEEDS_FILENAME)
    fetched_entries = get_all_entries(urls)

    entrymap = {}
    c = {}

    answers = load_ratings(RATING_FILENAME)

    if answers:
        vectorizer = get_vectorizer(answers.values())
        vectors = get_vectors(answers.values(), vectorizer)

        transformer = TfidfTransformer()
        features = transformer.fit_transform(vectors)

        linreg = LinearRegression()
        targets = scipy.array([1 if ans['rating'] == 'y' else 0 for ans in answers.values()])
        linreg.fit(features, targets)

    new_entries = {entry for entry in fetched_entries if entry.link not in answers}
    print(f'Found {len(new_entries)} new entries, {len(answers)} old entries.')

    new_answers = {}
    print('Are these titles interesting? [y/n]')
    for i, entry in enumerate(new_entries, start=1):

        prompt = f'{i}/{len(new_entries)} | {entry.title}: [y/n] '

        if answers:
            new_vect = vectorizer.transform([entry.title])
            new_vect2 = transformer.transform(new_vect)
            hod = linreg.predict(new_vect2)[0]

            percent = int(round(hod * 100))
            print(f'Predicted value: {percent}%')

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


def get_vectorizer(entries):
    titles = [doc["title"] for doc in entries]
    vect = CountVectorizer()
    vect.fit(titles)
    return vect


def get_vectors(entries, vectorizer):
    titles = [doc["title"] for doc in entries]
    return vectorizer.transform(titles)


def save_ratings(answers, filename):
    with open(filename, 'w') as fd:
        yaml.dump(answers, fd)


def load_ratings(filename):
    try:
        with open(filename, 'r') as fd:
            return yaml.load(fd)
    except FileNotFoundError:
        return {}


if __name__ == '__main__':
    main()
