# neighborhood

Server and CLI that can turn an SF street address into an SF neighborhood.

To regenerate the data, download the ["Street Data Extract" data set](https://sfelections.org/tools/election_data/dataset.php?ATAB=d1970-01-01) and
run:

```bash
cd data
./join_data.py elections-data.txt precincts.tsv | gzip > ../src/data/neighborhood_data.tsv.gz
```

This can be tested on the command line via:

```bash
./src/find_neighborhood.py "123 Main St"
```

This can be run as a server via:

```bash
./tools/run_server.sh
```

And accessed via:

<http://localhost:8080/sf?address=123+Main+St>

This can be run as a Docker container:

```bash
./tools/run_docker_server.sh
```
