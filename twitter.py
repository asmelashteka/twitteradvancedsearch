import sys
import json
import requests
from requests_oauthlib import OAuth1
import credentials
import time
import random

PROXIES = {'http': 'http://teka:130.75.87.215:5555',
           'https': 'https://teka:130.75.87.215:5555'}

class REST_API(object):
    """Twitter REST API."""
    def __init__(self, key, end_point):
        self.key       = key
        self.end_point = end_point
        self.url       = self.set_url()
        self.session   = self.set_session()

    def set_url(self):
        if self.end_point == 'status_lookup':
            return 'https://api.twitter.com/1.1/statuses/lookup.json'

    def set_session(self):
        keys = credentials.get_keys(self.key)
        s = requests.Session()
        s.auth = OAuth1(**keys)
        return s

    def get(self, ids):
        payload = dict(id=ids)
        s = self.session.get(url=self.url, params=payload)
        for tweet in s.iter_lines():
            if not tweet: continue
            yield json.loads(tweet.decode('utf-8'))

    def post(self, ids):
        time.sleep(4)
        payload = dict(id=ids)
        s = self.session.post(url=self.url, data=payload)
        return s.json()


class STREAMING_API(object):
    """Twitter streaming API.
    https://dev.twitter.com/streaming/overview/request-parameters
    """
    def __init__(self, key, lang=None, end_point='filter'):
        self.key       = key
        self.lang      = lang
        self.end_point = end_point
        self.session   = self.set_session()

    def set_session(self):
        keys = credentials.get_keys(self.key)
        s = requests.Session()
        s.auth = OAuth1(**keys)
        return s

    def get_stream(self, keywords):
        """Track semantics A comma-separated list of phrases
        e.g. 'the twitter' is the AND twitter, and 'the,twitter' is the OR twitter
        """
        keywords = ','.join(keywords)
        if self.lang and self.lang != 'all':
            parameters = dict(track=keywords, language=self.lang)
        else:
            parameters = dict(track=keywords)
        if self.end_point == 'sample':
            url = 'https://stream.twitter.com/1.1/statuses/sample.json'
            return self.session.get(url, stream=True)

        elif self.end_point == 'filter':
            url = 'https://stream.twitter.com/1.1/statuses/filter.json'
            return self.session.post(url, data=parameters, stream=True)

        elif self.end_point == 'search':
            url = 'https://stream.twitter.com/1.1/statuses/search.json'
            return self.session.post(url, data=parameters, stream=True)

    def gen_tweets(self, keywords):
        self.stream = self.get_stream(keywords)
        sys.stderr.write('{} {} {}\n'.format(time.asctime(), self.stream.url, keywords))
        for item in self.stream.iter_lines():
            if item:
                try:
                    tweet = json.loads(item.decode('utf-8'))
                except:
                    continue
                else:
                    yield(tweet)

    def run(self, keywords=None):
        # to re-connect when connection is dropped
        # observed with requests.exceptions.ChunkedEncodingError:
        # workaround
        # https://github.com/ryanmcgrath/twython/issues/288
        while True:
            try:
                for tweet in self.gen_tweets(keywords):
                    yield(tweet)
            except:
                raise
                e = sys.exc_info()[0]
                sys.stderr.write('{} {} {} {}\n'.format(
            time.asctime(), str(e), self.end_point, self.key))

    def close(self):
        try:
            self.stream.close()
        except:
            pass


def test_one_long_query(duration):
    start_time = time.time()
    s = STREAMING_API(key=1, lang='en')
    keywords = set(['fb', 'twitter'])
    for tweet in s.run(keywords):
        print(tweet)
        if time.time() - start_time > duration:
            break
    return time.time() - start_time > duration


def test_several_short_queries(duration, times=10):
    s = STREAMING_API(key=1, lang='en')
    keywords = [set(['fb']), set(['twitter'])]*100
    init_time = time.time()
    start_time = time.time()
    counter = 0
    while True:
        idx = random.randint(0, len(keywords) - 1)
        seed = keywords[idx]
        sys.stderr.write('{} {} {}\n'.format(time.asctime(), idx, seed))
        for tweet in s.run(keywords=seed):
            print(tweet)
            if time.time() - start_time > duration:
                break
        s.close()
        time.sleep(1)
        start_time = time.time()
        counter += 1
        if counter > times: break
    return (time.time() - init_time) > duration*times + times


def test():
    assert test_one_long_query(600)
    assert test_several_short_queries(10, 10)


if __name__ == '__main__':
    test()
