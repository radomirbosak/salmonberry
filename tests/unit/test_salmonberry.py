import yaml
import pytest
import mock

from salmonberry import download, label


@pytest.fixture()
def mock_feedparse(monkeypatch):
    def parse(url):
        return mock.Mock(entries=[{'id': 'entry2'}, {'id': 'entry3'}])
    monkeypatch.setattr('feedparser.parse', parse)


def test_download(tmpdir, mock_feedparse):
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

@pytest.fixture()
def mock_get_unlabeled(monkeypatch):
    pass  #monkeypatch.setattr()

def test_label(tmpdir, mock_get_unlabeled):
    cachefile = tmpdir / 'cache.yaml'
    cachefile.write('- {id: entry1}\n- {id: entry2}')


    labelsfile = tmpdir / 'labels.yaml'
    labels = [{'id': 'entry1', 'labels': ['l1']}]
    labelsfile.write(yaml.dump(labels))

    label(cachefile, labelsfile)

    content = labelsfile.read()
    #assert content == ''
