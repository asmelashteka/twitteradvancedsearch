## Twitter Advanced Search Wrapper

This tool is a wrapper around [Twitter Advanced Search] (https://twitter.com/search-advanced)

## Usage Examples:

## Searching with hashtags

To screen-scrape the resulting tweets for a query with the hashtags \#charlie
or \#hebdo since 2016-0701 until 2016-08-22. This will print json
representation of the output for the query parameters to the standard output.

```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2016-07-01 -u 2016-08-02
```

## Retrieving raw json tweets

To obtain the raw json tweets instead of the custom json output of the screen
scrapping, then add the flag --raw or -r for short when invoking the script.
Note that to retrieve raw tweets, you will need Twitter keys. Please modify
credentials.py with your appropriate keys.

```shell
$ python advancedsearch.py -ht "charlie hebdo" -s 2016-07-01 -u 2016-08-02 --raw
```

## Reading parameters from file

If you prefer to store your query parameters in a file and use it instead of
supplying them in the command line, you can do so by putting them in search.txt
inside the project directory. Then invoke the script with the mode flag set to
file.

```shell
$ python advancedsearch.py -mode file
```

## Searching for any keywords or symbols

Searching for any keywords, e.g., cashtags such as $AAPL. Note we need to
escape $ in $AAPL.

```shell
$ python advancedsearch.py -any \$AAPL -s 2016-07-01 -u 2016-08-02
```

## More options (help)
For more options supported by the tool run:

```shell
$ python advancedsearch.py -h
```

Please send any bugs or feature requests to teka@L3S.de.
