import sys
import os
import json
import time
import random
import datetime
import argparse
import configparser
from collections import namedtuple
from queue import Queue
from threading import Thread

import requests
from bs4 import BeautifulSoup

from twitter import REST_API


class AdvancedSearch():
    """This class provides access to historic tweets.
    It achieves this by combining
    (i) a wrapper to Twitter advanced search,
    https://twitter.com/search-advanced and
    (ii) Twitter statuses look-up REST API,
    https://dev.twitter.com/rest/reference/get/statuses/lookup
    """
    _sentinel   = object()

    def __init__(self, keys):
        self.keys = keys
        self.TWEET_IDS = Queue()
        self.TWEETS = Queue()

    def run(self, payload, daily=False):
        sink = sink_stdout()
        t1 = Thread(target=self.gen_tweet_ids, args=(payload, daily))
        t2 = Thread(target=self.gen_raw_tweets, args=(sink,))
        t1.start()
        t2.start()
        while True:
            yield self.TWEETS.get()

    def stop(self):
        self.TWEET_IDS.put(AdvancedSearch._sentinel)

    def gen_tweet_ids(self, payload, daily):
        """A thread that generates tweet ids for a historic search"""
        for tweet in AdvancedSearchWrapper().run(payload, daily):
            self.TWEET_IDS.put(tweet['tweet_id'])
        self.TWEET_IDS.put(AdvancedSearch._sentinel)

    def gen_chunks(self, n=100):
        ids = []
        while True:
            tweet_id = self.TWEET_IDS.get()
            if tweet_id is AdvancedSearch._sentinel:
                yield(ids)
                break
            ids.append(tweet_id)
            if len(ids) == n:
                yield(ids)
                ids = []

    def gen_raw_tweets(self, target):
        """A thread that given tweet id generates raw json tweets"""
        api = REST_API(keys=self.keys, end_point='status_lookup')
        for tweet_ids in self.gen_chunks():
            if tweet_ids == []: break
            tweet_ids = ','.join(tweet_ids)
            for tweet in api.post(ids=tweet_ids):
                target.send(tweet)
                self.TWEETS.put(tweet)


class AdvancedSearchWrapper():
    """This script is a wrapper to the Twitter advanced search,
    https://twitter.com/search-advanced
    It's intended to be used in combination with the status look-up API,
    https://dev.twitter.com/rest/reference/get/statuses/lookup
    to crawl past tweets starting right from the very first tweet.
    """

    TWEET = namedtuple(
            'TWEET',(
                'created_at',
                'user_id',
                'tweet_id',
                'tweet_text',
                'screen_name',
                'user_name',
                'retweet_count',
                'favorite_count')
            )

    def __init__(self):
        self.session = self.set_session()
        self.status = 'run'

    def set_session(self):
        user_agents = ['Opera/9.80 (X11; Linux x86_64; U; fr) Presto/2.9.168 Version/11.50',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
                'Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0',
                'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
                'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:10.0) Gecko/20100101 Firefox/10.0']
        s = requests.Session()
        s.headers.update({'User-Agent' : random.choice(user_agents)})
        return s

    def run(self, payload, daily=False):
        if daily:
            stream = self.daily_search(payload)
        else:
            stream = self.search(payload)
        for tweet in stream:
            yield(tweet)

    def stop(self):
        self.status = 'stop'

    def daily_search(self, payload):
        for prev_day, next_day in self.gen_days(
                payload.get('since'), payload.get('until')):
            payload['since'] = prev_day
            payload['until'] = next_day
            for tweet in self.search(payload):
                yield(tweet)

    def search(self, payload):
        self.url = 'https://twitter.com/search'
        payload = self.gen_payload(payload)
        r = self.session.get(self.url, params=payload)
        self.url = 'https://twitter.com/i/search/timeline'
        while True:
            html_result, min_position = self.parse_response(r)
            tweets = self.parse_result(html_result)
            if len(tweets) == 0: break
            for tweet in tweets:
                yield (tweet._asdict())
            time.sleep(random.random())
            if self.status == 'stop':
                break
            if not min_position:
                break
            payload['max_position'] = min_position
            r = self.session.get(self.url, params=payload)

    def gen_payload(self, args):
        """ generate Query string
        q: all "exact" any -none #ht lang:en from:f1 OR from:f2
        to:t1 OR to:t2 @m1 OR @m2 near:"Hanover, Lower Saxony" within:15mi
        since:2016-09-25 until:2016-09-30 :) :( ? include:retweets
        """
        q = []
        # words
        if args.get('allwords'):
            all_words = ' AND '.join([w for w in args['allwords'].split()])
            q.append(all_words)

        if args.get('anywords'):
            any_words = ' OR '.join([w for w in args['anywords'].split()])
            q.append(any_words)

        if args.get('exactphrase'):
            exact_phrase = '"' + args['exactphrase'].strip() + '"'
            q.append(exact_phrase)

        if args.get('nonewords'):
            none_words = ' '.join(['- ' + w for w in args['nonewords'].split()])
            q.append(none_words)

        if args.get('hashtags'):
            hashtags = ' OR '.join(['#' + h if h[0] != '#' else h
                for h in args['hashtags'].split()])
            q.append(hashtags)

        # language
        if args.get('lang'):
            q.append('lang:' + args['lang'])

        # people
        #TODO strip off @ if it exists in query for from and to users
        if args.get('fromusers'):
            from_users = ' OR '.join(['from:' + u
                for u in args['fromusers'].split()])
            q.append(from_users)

        if args.get('tousers'):
            to_users = ' OR '.join(['to:' + u
                for u in args['tousers'].split()])
            q.append(to_users)

        if args.get('mentionusers'):
            mention_users = ' OR '.join(['@' + u if u[0] != '@' else u
                for u in args['mentionusers'].split()])
            q.append(mention_users)

        # places
        if args.get('place'):
            q.append('near:' + args['place'])

        # dates
        if args.get('since'):
            q.append('since:' + args['since'])
        if args.get('until'):
            q.append('until:' + args['until'])

        if args.get('positive'):
            q.append(':)')

        if args.get('negative'):
            q.append(':(')

        if args.get('retweets'):
            q.append('include:retweets')

        payload = {'q': ' '.join(q)}
        return payload


    def parse_response(self, r):
        """given r a response object from requests
        return the html result and the min_position
        to iterate for next call
        """
        r_type = r.headers.get('content-type')
        if 'html' in r_type: # first call
            html_result = r.text
            min_position = self.get_min_position(html_result)
            max_position = self.get_max_position(html_result)
        elif 'json' in r_type: # subsequent calls
            j = json.loads(r.text)
            html_result = j.get('items_html')
            min_position = j.get('min_position')
        else:
            sys.stderr.write('{} not valid HTML or JSON response.\n'.format(r_type))
            exit(1)
        return (html_result, min_position)


    def get_max_position(self, t):
        """t is a string search result
        return maximum tweet id to iterate over next pages
        """
        cursor = 'data-max-position="'
        if cursor not in t:
            return None
        idx = t.find(cursor) + len(cursor)
        offset = t[idx:].find('"')
        max_position = t[idx:idx + offset]
        return max_position


    def get_min_position(self, t):
        """t is a string search result
        return minimum tweet id to iterate over next pages
        """
        cursor = 'data-min-position="'
        if cursor not in t:
            return None
        idx = t.find(cursor) + len(cursor)
        offset = t[idx:].find('"')
        min_position = t[idx:idx + offset]
        return min_position

    def parse_result(self, t):
        """t is a string search result
        parse userid, tweet id and other info from search result
        """
        tweets = []
        s = BeautifulSoup(t, 'html.parser')
        for e in s.findAll('div', {'class' : 'original-tweet'}):
            user_id     = e.get('data-user-id', '')
            tweet_id    = e.get('data-tweet-id', '')
            screen_name = e.get('data-screen-name', '')
            user_name   = e.get('data-name', '')
            tweet_text  = e.find('p').text
            created_at  = e.find('span', {'class':'_timestamp'}).get(
                    'data-time','')
            created_at  = str(datetime.datetime.fromtimestamp(int(created_at)))
            retweet_count = self.extract_val(e,
                    cls='ProfileTweet-action--retweet')
            favorite_count = self.extract_val(e,
                    cls='ProfileTweet-action--favorite')
            tweet = AdvancedSearchWrapper.TWEET(
                    created_at,
                    user_id,
                    tweet_id,
                    tweet_text,
                    screen_name,
                    user_name,
                    retweet_count,
                    favorite_count)
            tweets.append(tweet)
        return tweets

    def gen_days(self, since, until, nofdays=1):
        """Good idea for broad topics that generate lots of tweets
        This helps do it daily instead of the entire duration.
        Also enables retrieving from past to recent chronologically.
        """
        if not since:
            since = '2006-03-21' # First tweet ever
        if not until:
            until = str(datetime.date.today())

        since = datetime.datetime.strptime(since, '%Y-%m-%d')
        until = datetime.datetime.strptime(until, '%Y-%m-%d')

        while since < until:
            prev_day = datetime.datetime.strftime(since, '%Y-%m-%d')
            since += datetime.timedelta(days=nofdays)
            next_day = datetime.datetime.strftime(since, '%Y-%m-%d')
            yield (prev_day, next_day)

    def extract_val(self, e, cls):
        """extracts fovorite or retweet counts
        given BeautifulSoup node e, and class cls
        returns retweet or favorite count
        """
        count = 'NA'
        node = e.find('div', {'class': cls})
        if not node:
            return count
        count = getattr(node.find('div',
            {'class': 'IconTextContainer'}),'text', '').strip()
        return count

def coroutine(func):
    """Decorator: primes `func` by advancing to first `yield`"""
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start

@coroutine
def sink_stdout():
    while True:
        tweet = (yield)
        #print(json.dumps(tweet))


def read_config(fin):
    """Reads search parameters from file fin"""
    APP_DATA = os.path.dirname(os.path.abspath(__file__))
    res = {}
    with open(os.path.join(APP_DATA, fin), 'rb') as f:
        for line in f:
            line = line.decode('utf-8').strip()
            if line == '' or line[0] == '#' or line[-1] == '=': continue
            key, val = line.split('=')
            res[key.strip().lower()] = val.strip()
    return res


def check_payload(args):
    try:
        since = args.get('since')
        if since:
            datetime.datetime.strptime(since, '%Y-%m-%d')
        until = args.get('until')
        if until:
            datetime.datetime.strptime(since, '%Y-%m-%d')
    except ValueError:
        raise('ERROR. Day should be in yyyy-mm-dd format.\n')


def read_payload(args):
    # script input mode: from command line vs file
    if args.mode == 'cmd':
        payload = vars(args)
    else:
        payload = read_config(args.fin)

    check_payload(payload)
    return payload

def read_config(key='default', fin='credentials.cfg'):
    config = configparser.ConfigParser()
    config.read(fin)
    mapping = {'consumer_key'        : 'client_key',
               'consumer_secret'     : 'client_secret',
               'access_token'        : 'resource_owner_key',
               'access_token_secret' : 'resource_owner_secret'}
    credentials = {}
    for token in config[key]:
        value = config[key].get(token)
        _key = mapping.get('_'.join(token.split()))
        credentials[_key] = value
    return credentials


def read_args():
    """ expose functionalities in https://twitter.com/search-advanced
    as much as possible
    """
    parser = argparse.ArgumentParser(description='Twitter search advanced.')

    parser.add_argument('-all',  '--allwords', help='all of these words')
    parser.add_argument('-any',  '--anywords', help='any of these words')
    parser.add_argument('-d', '--daily', help='daily search from past to recent.',
            action='store_true')
    parser.add_argument('-exact','--exactphrase', help='this exact phrase')
    parser.add_argument('-fusers',  '--fromusers', help='from these accounts')
    parser.add_argument('-f', '--fin', help='input file if mode is file',
            default='search.txt')
    parser.add_argument('-ht', '--hashtags', help='these hashtags')
    parser.add_argument('-k', '--key', help='Twitter key in credentials.txt',
            default='default')
    parser.add_argument('-l',  '--lang', help='written in language')
    parser.add_argument('-musers',  '--mentionusers', help='mentioning these accounts')
    parser.add_argument('-m', '--mode', help='input from cmd or file',
            choices=['file','cmd'], default='cmd')
    parser.add_argument('-neg',  '--negative', help='select negative :(',
            choices=[True, False])
    parser.add_argument('-none', '--nonewords', help='none of these words')
    parser.add_argument('-p',  '--place', help='near this place')
    parser.add_argument('-pos',  '--positive', help='select positive :)',
            choices=[True, False])
    parser.add_argument('-r',  '--raw', help='download raw tweet',
            action='store_true')
    parser.add_argument('-rt', '--retweets', help='include retweets',
            choices=[True, False])
    parser.add_argument('-s',  '--since', help='since date yyyy-mm-dd')
    parser.add_argument('-tusers',  '--tousers', help='to these accounts')
    parser.add_argument('-u',  '--until', help='until date yyyy-mm-dd')

    args = parser.parse_args()
    return args



def main():
    args = read_args()
    payload = read_payload(args)
    keys = read_config(args.key)

    if args.raw:
        stream = AdvancedSearch(keys)
    else:
        stream = AdvancedSearchWrapper()

    for tweet in stream.run(payload, args.daily):
        print(json.dumps(tweet))


if __name__ == '__main__':
    main()
