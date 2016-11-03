import sys
import os
import json
import time
import random
import argparse
import datetime
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

    def __init__(self, key=1):
        self.twitter_key = key
        self.TWEET_IDS = Queue()
        self.TWEETS = Queue()

    def run(self, payload):
        sink = sink_stdout()
        t1 = Thread(target=self.gen_tweet_ids, args=(payload,))
        t2 = Thread(target=self.gen_raw_tweets, args=(sink,))
        t1.start()
        t2.start()
        while True:
            yield self.TWEETS.get()

    def stop(self):
        self.TWEET_IDS.put(AdvancedSearch._sentinel)

    def gen_tweet_ids(self, payload):
        """A thread that generates tweet ids for a historic search"""
        s = AdvancedSearchWrapper()
        for tweet in s.run(payload):
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
        api = REST_API(key=self.twitter_key, end_point='status_lookup')
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
    TWEET = namedtuple('TWEET', 'created_at, user_id, tweet_id, tweet_text, screen_name, user_name, rt_cnt, fv_cnt')

    def __init__(self, url='https://twitter.com/search'):
        self.url = url
        self.session = self.set_session()
        self.status = 'run'

    def set_session(self):
        user_agents = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
                       'Opera/9.80 (X11; Linux x86_64; U; fr) Presto/2.9.168 Version/11.50']
        s = requests.Session()
        s.headers.update({'User-Agent' : random.choice(user_agents)})
        return s

    def run(self, payload):
        r = self.session.get(self.url, params=payload)
        self.url = 'https://twitter.com/i/search/timeline'
        while True:
            #sys.stderr.write('{} {}\n'.format(time.asctime(), r.url))
            html_result, min_position = self.parse_response(r)
            sys.stderr.write('{} {}\n'.format(time.asctime(), min_position))
            tweets = self.parse_result(html_result)
            if len(tweets) == 0: break
            for tweet in tweets:
                yield (tweet._asdict())
            time.sleep(random.random())
            payload['max_position'] = min_position
            if self.status == 'stop':
                break
            r = self.session.get(self.url, params=payload)

    def stop(self):
        self.status = 'stop'

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

            sys.stderr.write('-----------\n')
            sys.stderr.write('{}\n'.format(min_position))
            sys.stderr.write('{}\n'.format(max_position))
            sys.stderr.write('-----------\n')

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
            created_at  = e.find('span', {'class':'_timestamp'}).get('data-time','')
            created_at  = str(datetime.datetime.fromtimestamp(int(created_at)))
            rt_cnt = self.extract_val(e, cls='ProfileTweet-action--retweet')
            fv_cnt = self.extract_val(e, cls='ProfileTweet-action--favorite')
            tweet = AdvancedSearchWrapper.TWEET(created_at, user_id, tweet_id,
                    tweet_text, screen_name, user_name, rt_cnt, fv_cnt)
            tweets.append(tweet)
        return tweets

    def gen_seq_days(self, since, until, nofdays=1):
        """Good idea for broad topics that generate lots of tweets
        This helps do it daily instead of the entire duration
        """
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


def verify_date_format(s):
    try:
        datetime.datetime.strptime(s, '%Y-%m-%d')
    except ValueError:
        return False
    return True

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


def gen_payload(args):
    """ generate Query string
    q: all "exact" any -none #ht lang:en from:f1 OR from:f2
    to:t1 OR to:t2 @m1 OR @m2 near:"Hanover, Lower Saxony" within:15mi
    since:2016-09-25 until:2016-09-30 :) :( ? include:retweets
    """

    if not(args.get('allwords')    or \
           args.get('exactphrase') or \
           args.get('anywords')    or \
           args.get('nonewords')   or \
           args.get('hashtags')):
        sys.stderr.write('No search terms.\n')
        exit(1)

    if not verify_date_format(args.get('since')) or \
            not verify_date_format(args.get('until')):
        sys.stderr.write('provide --since or --until in yyyy-mm-dd format\n')
        exit(1)

    q = []
    # words
    if args.get('allwords'):
        args['allwords'] = ' AND '.join([w for w in args['allwords'].split()])

    if args.get('exactphrase'):
        args['exactphrase'] = '"' + args['exactphrase'].strip() + '"'

    if args.get('anywords'):
        args['anywords'] = ' OR '.join([w for w in args['anywords'].split()])

    if args.get('nonewords'):
        args['nonewords'] = ' '.join(['- ' + w for w in args['nonewords'].split()])

    if args.get('hashtags'):
        args['hashtags'] = ' OR '.join(
                ['#' + h if h[0] != '#' else h for h in args['hashtags'].split()])
    words = 'allwords anywords exactphrase nonewords hashtags'.split()
    q += [args[k] for k in words if args[k]]

    # language
    if args.get('lang'):
        q += ['lang:' + args['lang']]

    # people
    #TODO strip off @ if it exists in query for from and to users
    if args.get('fromusers'):
        args['fromusers'] = ' OR '.join(['from:' + u for u in args['fromusers'].split()])

    if args.get('tousers'):
        args['tousers'] = ' OR '.join(['to:' + u for u in args['tousers'].split()])

    if args.get('mentionusers'):
        args['mentionusers'] = ' OR '.join(
                ['@' + u if u[0] != '@' else u for u in args['mentionusers'].split()])
    people = 'fromusers tousers mentionusers'.split()
    q += [args[k] for k in people if args[k]]

    # places
    if args.get('place'):
        q += ['near:' + args['place']]

    # dates
    # TODO default date from now backwards if argument not given
    q += ['since:' + args['since'], 'until:' + args['until']]

    if args.get('positive'):
        q += [':)']

    if args.get('negative'):
        q += [':(']

    if args.get('retweets'):
        q += ['include:retweets']

    payload = {'q': ' '.join(q)}
    return payload


def read_payload(args):
    # script input mode: from command line vs file
    if args.mode == 'cmd':
        payload = gen_payload(vars(args))
    else:
        payload = gen_payload(read_config(args.fin))
    return payload


def read_args():
    """ expose functionalities in https://twitter.com/search-advanced
    as much as possible
    """
    parser = argparse.ArgumentParser(description='Twitter search advanced.')

    parser.add_argument('-all',  '--allwords', help='all of these words')
    parser.add_argument('-any',  '--anywords', help='any of these words')
    parser.add_argument('-exact','--exactphrase', help='this exact phrase')
    parser.add_argument('-fusers',  '--fromusers', help='from these accounts')
    parser.add_argument('-f', '--fin', help='input file if mode is file', default='search.txt')
    parser.add_argument('-ht', '--hashtags', help='these hashtags')
    parser.add_argument('-k', '--key', help='Twitter key entry to credentials.txt', default=1)
    parser.add_argument('-l',  '--lang', help='written in language')
    parser.add_argument('-musers',  '--mentionusers', help='mentioning these accounts')
    parser.add_argument('-m', '--mode', help='input from cmd or file', choices=['file','cmd'], default='cmd')
    parser.add_argument('-neg',  '--negative', help='select negative :(', choices=[True, False])
    parser.add_argument('-none', '--nonewords', help='none of these words')
    parser.add_argument('-p',  '--place', help='near this place')
    parser.add_argument('-pos',  '--positive', help='select positive :)', choices=[True, False])
    parser.add_argument('-r',  '--raw', help='download raw tweet', action='store_true')
    parser.add_argument('-rt', '--retweets', help='include retweets', choices=[True, False])
    parser.add_argument('-s',  '--since', help='since date yyyy-mm-dd')
    parser.add_argument('-tusers',  '--tousers', help='to these accounts')
    parser.add_argument('-u',  '--until', help='until date yyyy-mm-dd')

    args = parser.parse_args()
    return args


def main():
    args = read_args()
    payload = read_payload(args)

    if args.raw: stream = AdvancedSearch(args.key)
    else: stream = AdvancedSearchWrapper()

    for tweet in stream.run(payload):
        print(json.dumps(tweet))


if __name__ == '__main__':
    main()
