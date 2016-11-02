# Twitter Advanced Search

This tool is a wrapper around [Twitter Advanced Search]
(https://twitter.com/search-advanced)

## Usage Examples:

## Searching with hashtags

To screen-scrape the resulting tweets for a query with the hashtags \#charlie
or \#hebdo since 2016-0701 until 2016-08-22. This will print json
representation of the output for the query parameters to the standard output.

```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2015-01-06 -u 2016-02-06
```

## Retrieving raw json tweets

To obtain the raw json tweets instead of the custom json output of the screen
scrapping, then add the flag --raw or -r for short when invoking the script.
Note that to retrieve raw tweets, you will need Twitter keys. Please modify
credentials.py with your appropriate keys.

```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2015-01-06 -u 2016-02-06 --raw
```

## Reading parameters from file

If you prefer to store your query parameters in a file and use it instead of
supplying them in the command line, you can do so by putting them in search.txt
inside the project directory. Then invoke the script with the mode flag set to
file.

```shell
$ python advancedsearch.py -mode file
```

## Searching for keywords or symbols

Searching for any keywords, e.g., cashtags such as $AAPL. Note we need to
escape $ in $AAPL if we're calling the script from the command line.

```shell
$ python advancedsearch.py -any \$AAPL -s 2016-07-01 -u 2016-08-02
```

## More options (help)
For more options supported by the tool run:

```shell
$ python advancedsearch.py -h
```


## [Search Operators] (https://twitter.com/search-home#)

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
