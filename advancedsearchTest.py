import unittest
from datetime import datetime, timezone

from advancedsearch import name2keys, AdvancedSearch, AdvancedSearchWrapper

TWITTER_DATE_FORMAT = '%a %b %d %H:%M:%S %z %Y'


class TestAdvancedSearch(unittest.TestCase):

    def setUp(self):
        self.keys = name2keys(key='1')
        self.stream = AdvancedSearch(self.keys)

    def test_location(self):
        payload = {'location': 'Berlin, Germany'}


    def test_language(self):
        payload = {'q': '#charlie OR #hebdo since:2015-01-06 until:2016-02-06'}
        pass

    def test_tweet_fields(self):
        pass

    def test_user_fields(self):
        pass


class TestAdvancedSearchWrapper(unittest.TestCase):

    def setUp(self):
        self.stream = AdvancedSearchWrapper()
        self.MAX_TWEETS = 500

    def test_date(self):
        since = datetime.strptime('2015-01-06 00:00:00',
                '%Y-%m-%d %H:%M:%S')
        until = datetime.strptime('2016-02-06 23:59:59',
                '%Y-%m-%d %H:%M:%S')
        payload = {'hashtags': 'charlie hebdo',
                   'since': '2015-01-06 00:00:00',
                   'until': '2016-02-06 00:00:00'}
        # make since and until timezone aware
        since = since.replace(tzinfo=timezone.utc)
        until = until.replace(tzinfo=timezone.utc)
        for idx, tweet in enumerate(self.stream.run(payload)):
            if idx == self.MAX_TWEETS:
                self.stream.stop()
                break
            created_at = datetime.strptime(tweet['created_at'],
                    TWITTER_DATE_FORMAT)
            self.assertTrue(since <= created_at and created_at <= until)

    def test_hashtags(self):
        payload = {'hashtags': 'charlie hebdo',
                   'since': '2015-01-06 00:00:00',
                   'until': '2016-02-06 00:00:00'}
        for idx, tweet in enumerate(self.stream.run(payload)):
            if idx == self.MAX_TWEETS: break
            tweet_text = tweet.get('tweet_text').lower()
            self.assertTrue('charlie' in tweet_text or 'hebdo' in tweet_text)

    def test_location_default(self):
        '''adds within:15mi'''
        payload = {'place': 'Berlin, Germany',
                   'since': '2016-12-19 20:00:00',
                   'until': '2016-12-19 23:59:59'}
        count = 0
        for idx, tweet in enumerate(self.stream.run(payload)):
            if idx > self.MAX_TWEETS:
                break
            tweet_text = tweet.get('tweet_text').lower()
            count = idx + 1
        print('Berlin, Germany {}'.format(count))

    def test_location_within(self):
        '''explicit within'''
        payload = {'place': 'Germany',
                   'within': '',
                   'since': '2016-12-19 20:00:00',
                   'until': '2016-12-19 23:59:59'}
        count = 0
        for idx, tweet in enumerate(self.stream.run(payload)):
            if idx > self.MAX_TWEETS:
                break
            tweet_text = tweet.get('tweet_text').lower()
            #self.assertTrue('berlin' in tweet_text)
            count = idx + 1
        print('Germany {}'.format(count))



    def xtest_from_people(self):
        payload = {'fromusers': 'hillaryclinton realdonaldtrump'}
        for idx, tweet in enumerate(self.stream.run(payload)):
            if idx == self.MAX_TWEETS: break
            screen_name = tweet.get('screen_name').strip().lower()

            self.assertTrue(screen_name in ('hillaryclinton', 'realdonaldtrump'))


if __name__ == '__main__':
    unittest.main()
