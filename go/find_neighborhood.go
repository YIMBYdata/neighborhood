package main

import (
	"compress/gzip"
	"encoding/csv"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"
	"strings"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

type record struct {
	side             string
	lo, hi, district int
	neighborhood     string
}

func newRecord(line []string) (*record, error) {
	lo, err := strconv.Atoi(line[3])
	if err != nil {
		return nil, err
	}
	hi, err := strconv.Atoi(line[4])
	if err != nil {
		return nil, err
	}
	district, err := strconv.Atoi(line[5])
	if err != nil {
		return nil, err
	}
	return &record{line[2], lo, hi, district, line[6]}, nil
}

func (r *record) matches(streetNum int) bool {
	if (r.side == "E" && streetNum%2 == 1) ||
		(r.side == "O" && streetNum%2 == 0) {
		return false
	}
	if r.side == "A" {
		return true
	}
	return r.lo <= streetNum && streetNum <= r.hi
}

type database struct {
	records map[string]map[string][]record
}

func openFile(filename string) (io.Reader, error) {
	f, err := os.Open(filename)
	if err == nil && strings.HasSuffix(filename, ".gz") {
		return gzip.NewReader(f)
	}
	return f, err
}

func parseTsvFile(filename string) ([][]string, error) {
	f, err := openFile(filename)
	if err != nil {
		return nil, err
	}
	r := csv.NewReader(f)
	r.Comma = '\t'
	return r.ReadAll()
}

func newDatabase(filename string) (*database, error) {
	lines, err := parseTsvFile("../app/data/neighborhood_data.tsv.gz")
	if err != nil {
		return nil, err
	}

	db := database{map[string]map[string][]record{}}
	for i, line := range lines {
		if i == 0 {
			continue
		}
		r, err := newRecord(line)
		if err != nil {
			return nil, err
		}
		typeMap := db.records[line[0]]
		if typeMap == nil {
			typeMap = map[string][]record{}
			db.records[line[0]] = typeMap
		}
		records := typeMap[line[1]]
		if records == nil {
			records = []record{}
			typeMap[line[1]] = records
		}
		typeMap[line[1]] = append(records, *r)
	}
	return &db, nil
}

func (db *database) findMatches(streetNum int, streetName string, streetType string) []record {
	typeMap := db.records[streetName]
	records := typeMap[streetType]
	if len(records) == 0 {
		records = []record{}
		for _, v := range typeMap {
			records = append(records, v...)
		}
	}
	matches := []record{}
	for _, r := range records {
		if r.matches(streetNum) {
			matches = append(matches, r)
		}
	}
	return matches
}

func main() {
	db, err := newDatabase("../app/data/neighborhood_data.tsv.gz")
	check(err)

	streetNum, err := strconv.Atoi(os.Args[1])
	check(err)
	fmt.Println(db.findMatches(streetNum, strings.ToLower(os.Args[2]), strings.ToLower(os.Args[3])))

	handler := func(w http.ResponseWriter, _ *http.Request) {
		io.WriteString(w, "Hello from a HandleFunc #1!\n")
	}
	http.HandleFunc("/sf/district", handler)
	http.ListenAndServe(":8080", nil)
}
