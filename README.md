## Twitter Advanced Search Wrapper

This tool is a wrapper around [Twitter Advanced Search] (https://twitter.com/search-advanced)

## Usage examples:

## tweets containing hashtags

To screen-scrape the resulting tweets for a query with the hashtags \#charlie
or \#hebdo since 2016-0701 until 2016-08-22. This will print json
representation of the output for the query parameters to the standard output.


python advancedsearch.py -ht "charlie hebdo" -s 2016-07-01 -u 2016-08-02


## raw json tweets

To obtain the raw json tweets instead of the custom json output of the screen
scrapping, then add the --raw flag or -r flag when invoking the script.

python advancedsearch.py -ht "charlie hebdo" -s 2016-07-01 -u 2016-08-02 --raw


## reading parameters from file

If you prefer to store your query parameters in a file and use it instead of
supplying them in the command line, you can do so by putting them in search.txt
inside the project directory. Then invoke the script with the mode flag set to
file.

python advancedsearch.py -mode file

## searching for any keywords or symbols

Searching for any keywords, e.g., cashtags such as $AAPL. Note we need to
escape $ in $AAPL.

python advancedsearch.py -any \$AAPL -s 2016-07-01 -u 2016-08-02


## more options (help)
For more options supported by the tool run:

python advancedsearch.py -h


NOTE:
- For raw tweets, you will need Twitter keys. Please modify credentials.py with
  your appropriate keys.


Please send any bugs or feature requests to teka@L3S.de.
