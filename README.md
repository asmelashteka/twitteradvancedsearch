# Twitter Advanced Search

This tool is a wrapper around [Twitter Advanced Search]
(https://twitter.com/search-advanced).

## Usage Examples:

## Searching with hashtags

To search tweets containing a set of hashtags, use the flag `-ht` or
`--hashtag` followed by the list of hashtags, inside quotation marks if there
is more than one. To indicate date range, use `--since` or `-s` and `--until`
or `-u`. E.g., to gather tweets with hashtags **\#charlie"** or **\#hebdo**
from 2016-07-01 to 2016-08-22.

```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2015-01-06 -u 2016-02-06
```

Note that the resulting output is a custom json format containing the fields:
` created_at, user_id, tweet_id, tweet_text, screen_name, user_name,
retweet_count, and favorite_count`.

## Retrieving raw json tweets

In order to obtain the complete raw json tweets from the Twitter REST API, you
need Twitter API credentials. Check [Twitter oauth
overview](https://dev.twitter.com/oauth/overview) for details. After obtaining
credentials, modify the `credentials.py` by substituting the corresponding
fields. You can specify multiple credentials. To use a specific credential,
run the script with the flag `--raw` or `-r` for short and the corresponding
dictionary key in `credentials.py`.

```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2015-01-06 -u 2016-02-06 --raw -k 0
```

## Reading parameters from file

If you prefer to store your query parameters in a file and use that instead of
supplying them in the command line, use the flag `-mode file`. Modify the query
parameters inside the `search.txt` in the project directory according to your
requirements.

```shell
$ python advancedsearch.py -mode file
```

## Searching with keywords or symbols

To search tweets containing any keyword, use `-any` followed by the keywords.
E.g., to collect tweets with the cashtag $AAPL, we need to escape $ in $AAPL
when calling the script from the command line.

```shell
$ python advancedsearch.py -any \$AAPL -s 2016-07-01 -u 2016-08-02
```

## Retrieving in Chronological order

If you want to retrieve tweets in chronological order from past to recent.
Supply the `--daily` flag.

```shell
$ advancedsearch.py -ht kdd2016 -s 2016-01-02 -u 2016-11-01 --daily
```

## More options (help)

To find out more options supported by the tool run:

```shell
$ python advancedsearch.py -h
```


## Search Operators

The following documentation on operators in Advanced Search is taken from the
page [Search Operators](https://twitter.com/search-home#) which is buried
under the link `operators`. Read more about [Using advanced search]
(https://support.twitter.com/articles/71577).

| Operator         |  Finds tweets...    
|------------------|---------------------
| twitter search   |  containing both "twitter" and "search". This is the default operator.
| "happy hour"     |  containing the exact phrase "happy hour".
| love OR hate     |  containing either "love" or "hate" (or both).
| beer -root       |  containing "beer" but not "root".
| \#haiku          |  containing the hashtag "haiku".
| from:alexiskold  |  sent from person "alexiskold".
| to:techcrunch    |  sent to person "techcrunch".
| @mashable        |  referencing person "mashable".
| "happy hour"  near:"san francisco"  | containing the exact phrase "happy hour" and sent near "san francisco".
| near:NYC within:15mi                |  sent within 15 miles of "NYC".
| superhero since:2010-12-27          |  containing "superhero" and sent since date "2010-12-27" (year-month-day).
| ftw until:2010-12-27                |  containing "ftw" and sent up to date "2010-12-27".
| movie -scary :)                     |  containing "movie", but not "scary", and with a positive attitude.
| flight :(                           |  containing "flight" and with a negative attitude.
| traffic ?                           |  containing "traffic" and asking a question.
| hilarious filter:links              |  containing "hilarious" and linking to URLs.
| news source:twitterfeed             |  containing "news" and entered via TwitterFeed
