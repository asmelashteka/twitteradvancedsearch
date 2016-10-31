import unittest

from advancedsearch import AdvancedSearch, AdvancedSearchWrapper


class TestAdvancedSearch(unittest.TestCase):

    def setUp(self):
        self.stream = AdvancedSearch(raw=True, key=1)

    def test_date(self):
        pass

    def test_term(self):
        pass

    def test_people(self):
        pass

    def test_location(self):
        pass

    def test_lang(self):
        pass


class TestAdvancedSearchWrapper(unittest.TestCase):

    def setUp(self):
        self.stream = AdvancedSearchWrapper()

    def test_date(self):
        pass

    def test_term(self):
        pass

    def test_people(self):
        pass

    def test_location(self):
        pass

    def test_lang(self):
        pass


if __name__ == '__main__':
    unittest.main()
