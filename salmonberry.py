import feedparser

url = 'https://www.reddit.com/r/MachineLearning/.rss'

feed = feedparser.parse(url)


for i, entry in enumerate(feed.entries, start=1):
    print(f'{i}) {entry.title}')
