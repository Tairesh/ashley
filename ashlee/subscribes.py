import feedparser
import urllib.error


def parse_link(url):
    try:
        return feedparser.parse(url)
    except urllib.error.URLError:
        return None
