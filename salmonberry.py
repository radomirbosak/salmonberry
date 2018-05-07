import logging
from collections import Counter

import yaml
import feedparser


logging.basicConfig(level=logging.DEBUG)


url = 'https://www.reddit.com/r/MachineLearning/.rss'
RATING_FILENAME = 'ratings.yaml'


def main():
    feed = feedparser.parse(url)
    entrymap = {}
    c = {}

    answers = get_answers(RATING_FILENAME)

    new_entries = {entry for entry in feed.entries if entry.id not in answers}
    print(f'Found {len(new_entries)} new entries')

    new_answers = {}
    print('Are these titles interesting? [y/n]')
    for i, entry in enumerate(new_entries, start=1):

        prompt = f'{i}/{len(new_entries)} | {entry.title}: [y/n] '

        try:
            answer = input(prompt)
        except EOFError:
            print()
            logging.debug('Exiting')
            break

        new_answers[entry.id] = answer

    c = Counter(new_answers.values())

    others = len(new_answers) - c["y"] - c["n"]
    print(f'yes: {c["y"]}, no: {c["n"]}, others: {others}')

    answers.update(new_answers)
    dump_answers(answers, RATING_FILENAME)


def dump_answers(answers, filename):
    with open(filename, 'w') as fd:
        yaml.dump(answers, fd)


def get_answers(filename):
    try:
        with open(filename, 'r') as fd:
            return yaml.load(fd)
    except FileNotFoundError:
        return {}


if __name__ == '__main__':
    main()
