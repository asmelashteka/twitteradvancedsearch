# Twitter Advanced Search

This tool is a wrapper around [Twitter Advanced
Search](https://twitter.com/search-advanced).

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
credentials, modify the `credentials.cfg` by substituting the corresponding
fields. You can specify multiple credentials. To use a specific credential,
run the script with the flag `--raw` or `-r` for short. This picks up the
`default` credentials in `credentials.cfg`.

```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2015-01-06 -u 2016-02-06 --raw
```

If you want to use a particular credential, then you specify the corresponding
name with the `--key` flag or `k` for short. E.g., to use credentials under
`another` in `credentials.cfg`.


```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2015-01-06 -u 2016-02-06 --raw -k another
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

## Breaking searches to be performed daily

If you want to retrieve tweets daily in order from past to recent.
Supply the `--daily` flag.

```shell
$ python advancedsearch.py -ht kdd2016 -s 2016-08-10 -u 2016-08-20 --daily
```


## Retrieving tweets in chronological order

If you want to retrieve tweets sorted in chronological order from past to recent.
Supply the `--chronological` flag.

```shell
$ python advancedsearch.py -ht kdd2016 -s 2016-08-10 -u 2016-08-20 --chronological
```

## More options (help)

To find out more options supported by the tool run:

```shell
$ python advancedsearch.py -h
```


## Search Operators

The following documentation on operators in Advanced Search is taken
from the page [Search Operators](https://twitter.com/search-home#)
which is buried under the link `operators`. Read more about [Using
advanced search](https://support.twitter.com/articles/71577).

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


## References

Please cite [1](#Sover!) if using this code for building a demo or [2](#real-time-adaptive-crawler) if using for crawling tweets for other purposes.

### [Sover! Social Media Observer](#Sover!)

[1] Hadgu, Asmelash Teka, Sallam Abualhaija, and Claudia Niederée. [*Sover! Social Media Observer.*](https://dl.acm.org/citation.cfm?id=3210173)

```
@inproceedings{hadgu2018sover,
  title={Sover! Social Media Observer},
  author={Hadgu, Asmelash Teka and Abualhaija, Sallam and Nieder{\'e}e, Claudia},
  booktitle={The 41st International ACM SIGIR Conference on Research \& Development in Information Retrieval},
  pages={1305--1308},
  year={2018},
  organization={ACM}
}
```

### [Real-time Adaptive Crawler for Tracking Unfolding Events on Twitter](#real-time-adaptive-crawler)

[2] Hadgu, Asmelash Teka, Sallam Abualhaija, and Claudia Niederée. [*Real-time Adaptive Crawler for Tracking Unfolding Events on Twitter*](#real-time-adaptive-crawler)

```
@article{hadgu2019real,
  title={Real-time Adaptive Crawler for Tracking Unfolding Events on Twitter},
  author={Hadgu, Asmelash Teka and Abualhaija, Sallam and Nieder{\'e}e, Claudia},
  journal={ISCRAM},
  year={2019}
}
```
