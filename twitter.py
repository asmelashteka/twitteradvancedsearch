import sys
import json
import requests
from requests_oauthlib import OAuth1
import time

PROXIES = {'http': 'http://teka:130.75.87.215:5555',
           'https': 'https://teka:130.75.87.215:5555'}

class REST_API(object):
    """Twitter REST API."""
    def __init__(self, keys, end_point):
        self.keys      = keys
        self.end_point = end_point
        self.url       = self.set_url()
        self.session   = self.set_session()

    def set_url(self):
        if self.end_point == 'status_lookup':
            return 'https://api.twitter.com/1.1/statuses/lookup.json'
        elif self.end_point == 'followers_ids':
            return 'https://api.twitter.com/1.1/followers/ids.json'
        elif self.endpoint == 'friends_ids':
            return 'https://api.twitter.com/1.1/friends/ids.json'
        elif self.endpoint == 'status_retweets':
            return 'https://api.twitter.com/1.1/statuses/retweets/:id.json'

    def set_session(self):
        s = requests.Session()
        s.auth = OAuth1(**self.keys)
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
