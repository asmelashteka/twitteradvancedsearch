import datetime
import unittest

from advancedsearch import AdvancedSearch, AdvancedSearchWrapper


class TestAdvancedSearch(unittest.TestCase):

    def setUp(self):
        self.stream = AdvancedSearch(key=1)

    def test_tweet_fields(self):
        pass

    def test_user_fields(self):
        pass


class TestAdvancedSearchWrapper(unittest.TestCase):

    def setUp(self):
        self.stream = AdvancedSearchWrapper()
        self.MAX_TWEETS = 10

    def test_date(self):
        since = datetime.datetime.strptime('2015-01-06 00:00:00', '%Y-%m-%d %H:%M:%S')
        until = datetime.datetime.strptime('2016-02-06 23:59:59', '%Y-%m-%d %H:%M:%S')
        payload = {'q': '#charlie OR #hebdo since:2015-01-06 until:2016-02-06'}
        for idx, tweet in enumerate(self.stream.run(payload)):
            if idx == self.MAX_TWEETS:
                self.stream.stop()
                break
            created_at = datetime.datetime.strptime(
                    tweet['created_at'], '%Y-%m-%d %H:%M:%S')

            self.assertTrue(since <= created_at and created_at <= until)

    def test_hashtags(self):
        payload = {'q': '#charlie OR #hebdo since:2015-01-06 until:2016-02-06'}
        for idx, tweet in enumerate(self.stream.run(payload)):
            if idx == self.MAX_TWEETS: break
            tweet_text = tweet.get('tweet_text').lower()

            self.assertTrue('charlie' in tweet_text or 'hebdo' in tweet_text)

    def test_people(self):
        pass

    def test_location(self):
        payload = {'q': '#charlie OR #hebdo since:2015-01-06 until:2016-02-06'}
        pass

    def test_lang(self):
        payload = {'q': '#charlie OR #hebdo since:2015-01-06 until:2016-02-06'}
        pass


if __name__ == '__main__':
    unittest.main()
