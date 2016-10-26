## Twitter Advanced Search Wrapper

This tool is a wrapper around [Twitter Advanced Search] (https://twitter.com/search-advanced)

## Usage examples:

(1) To screen-scrape the resulting tweets for a query with the hashtags
\#charlie or \#hebdo since 2016-0701 until 2016-08-22

python advancedsearch.py -ht "charlie hebdo" -s 2016-07-01 -u 2016-08-02

This will print json representation of the output for the query parameters to
the standard output


(2) If you want instead the raw json representing each tweet, then add the
--raw flag or -r flag when invoking the script

python advancedsearch.py -ht "charlie hebdo" -s 2016-07-01 -u 2016-08-02 --raw


(3) If you prefer to store your query parameters in a file instead of supplying
them in the command line, you can do so by putting them in search.txt file as
the example given. Then invoke the script with the mode flag set to file.

python advancedsearch.py -mode file > out


For more options supported by the tool run:
python advancedsearch.py -h


NOTE:
- For raw tweets, you will need twitter keys. Please modify credentials.py with
  your appropriate keys.


Please send any bugs or feature requests to teka@L3S.de.
