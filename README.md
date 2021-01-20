# neighborhood

Server and CLI that can turn an SF street address into an SF neighborhood.

To regenerate the data, download the ["Street Data Extract" data set](https://sfelections.org/tools/election_data/dataset.php?ATAB=d1970-01-01) and
run:

```bash
$ cd data
$ ./join_data.py elections-data.txt precincts.tsv | gzip > ../app/data/neighborhood_data.tsv.gz
```

This can be tested on the command line via:

```bash
$ cd py
$ ./app/find_neighborhood.py "123 Main St"
```

This can be run as a server via:

```bash
$ cd py/app
$ uvicorn main:app --reload
```

And accessed via:

<http://localhost:8000/sf?address=123+Main+St>

This can be run as a Docker container:

```bash
$ cd py
$ docker build -t neighborhood .
$ docker run --rm -it -p 8080:80 neighborhood
$ docker run -p 80:80 neighborhood
```
