import yaml
import pytest
import feedparser
import mock

from salmonberry import download


@pytest.fixture(autouse=True)
def mock_feedparse(monkeypatch):
    def parse(url):
        return mock.Mock(entries=[{'id': 'entry2'}, {'id': 'entry3'}])
    monkeypatch.setattr(feedparser, 'parse', parse)


def test_download(tmpdir):
    # prepare feed list
    feedlist = "---\n- 'https://www.reddit.com/r/MachineLearning/new/.rss'"
    feedfile = tmpdir.join('feeds.yaml')
    feedfile.write(feedlist)

    # prepare cache file
    cachefile = tmpdir / 'cache.yaml'
    cachefile.write('- {id: entry1}\n- {id: entry2}')

    # run the tested function
    download(feedfile, cachefile)

    assert cachefile.check(), 'Cache file does not exist'

    # Cache has three entries
    content = tmpdir.join('cache.yaml').read()
    dest_yaml = yaml.load(content)
    assert len(dest_yaml) == 3
