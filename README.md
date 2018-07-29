# neighborhood
Script for turning an SF street address to and SF neighborhood. Primarily intended for use in YIMBY Action Zapier.

To regenerate the data, download the Street Data Extract" data set
(https://sfelections.org/tools/election_data/dataset.php?ATAB=d1970-01-01) and
run:

```
$ ./join_data.py elections-data.txt data/precincts.tsv | gzip \
> neighborhood_data.tsv.gz
```

This can be tested on the command line via:

```
$ ./find_neighborhood.py data/neighborhood_data.tsv.gz "123 Main St"
```
