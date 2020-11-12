# deezer-stats

Visualize your Deezer listening habbits with this project.

## Feature

Export to an Elasticsearch stack to use Kibana's visualization mecanism.
Use the power of Python to get stats about the most listened artist, song, etc.

## How to use

### Elastic stack

Deploy the local Elasticsearch stack with a simple `docker-compose up -d`
Aims your browser to `localhost:5601` to access Kibana's UI.

### Prepare your data

Get your Deezer data by making a GDPR request to their privacy email, asking
specifically for the whole listening history.

They'll send you a big .xls containing everything. Export the listening history
tab to a TSV file (using google's sprreadsheet, excel or whatever).

The support response may take some time, be careful (legally at most 31 days)

### Run the script

Prepare your python venv, and simply run `./main.py <tsv file>`

### Import pre-built dashboards and vizu

`gunzip export.ndjson.gz` and import the ndjson file in Kibana's UI

# Example

## CLI

###### Get help

`./main.py -h`

###### Get your all-time top 50

`./main.py --top-track --top 50 ./history.tsv`

###### Get all the songs you've heard at least 100 times

`./main.py --min 100 ./history.tsv`

###### Get all the songs you've heard at least 10 times in decembre 2017

`./main.py --min 100 --date-after 2017-12-01 --date-before 2018-01-01 ./history.tsv`

###### Determine that a song heard is a song listened at least 30s

`./main.py --top-track --valid-algo min_30 ./history.tsv`

###### Get the song you've spent the most time listening to

`./main.py --top-track-by-time ./history.tsv`

###### Get the most listened artists

`./main.py --top-artists ./history.tsv`

###### Get the most listened artists by time

`./main.py --top-artists-by-time ./history.tsv`

###### Get the most listened artists by time and considered different artists for comma

`./main.py --top-artists-by-time --split-comma-separated-artists ./history.tsv`

For example, the results will be:
```
[  20]  929 times (2 days, 8:18:22 ): Claptone - from 2016-05-19 23:06:06 to 2020-10-18 23:14:11
```

instead of
```
[  41]  514 times (1 day, 4:48:43  ): Claptone                   - from 2016-05-19 23:06:06 to 2020-10-18 23:14:11
...
[  47]  355 times (1 day, 0:30:47  ): Claptone, Nathan Nicholson - from 2017-02-18 14:08:16 to 2020-10-18 22:41:20
...
```

###### Find the songs you liked back in 2017-01 but are not in your all-time favorites

```
./main.py --forgotten-hits \
  --forgotten-hits-start 2017-01-01 \ # Set the start period. Defaults to last year
  --forgotten-hits-end 2017-02-01 \ # Set the end period. Defaults to now
  --forgotten-hits-top 150 \ # Will yields the songs you liked the most that are not in your TOP 150 all-time
  --forgotten-hits-bucket-size 10 \ # Will give you 10 songs per month in the given period
  ./history.tsv
```

## Kibana's UI

Heatmap of when I listen to music in average during the week.
![](./heatmap-week.jpg)
