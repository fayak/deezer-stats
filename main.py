#!/usr/bin/env python3

import es
import json
from datetime import datetime
from datetime import timedelta
import csv
import sys

associations = {
        "title": "Song Title",
        "artist": "Artist",
        "ISRC": "ISRC",
        "album": "Album Title",
        "IP": "IP Address",
        "list_time": "Listening Time",
        "date": "Date",
}
keys = associations.keys()

# datetime.strptime(line[DATE], "%Y-%m-%d %H:%M:%S.000")

class Track(dict):
    def __repr__(self):
        return f"{self['title']} - {self['artist']} ({self.nb} listening)"

    def __init__(self, track):
        super().__init__({**track, "nb": 0, "list_time_sum": 0})
        self.__dict__ = self
        self += track

    def __add__(self, other):
        self.nb += 1
        self.list_time_sum += other.list_time
        return self

class Catalog():
    def __init__(self):
        self.tracks = {}

    def __add__(self, other):
        if other.ISRC in self.tracks:
            self.tracks[other.ISRC] += other
        else:
            self.tracks[other.ISRC] = Track(other)
        return self

    def __getitem__(self, key):
        return self.tracks[key.ISRC]

    def search(self, q):
        r = []
        q = q.upper()
        for _, track in self.tracks.items():
            if q in str(track.title).upper():
                r.append(track)
        return r

class ListTrack(dict):
    def __repr__(self):
        return f"[{self.date}] {str(timedelta(seconds=self.list_time))} - {self['title']} - {self['artist']}"

    def __init__(self, line):
        tmp_dict = {}
        for k, v in associations.items():
            if k == "list_time":
                tmp_dict[k] = int(line[v])
            elif k == "date":
                tmp_dict[k] = datetime.strptime(line[v], "%Y-%m-%d %H:%M:%S.000")
            else:
                tmp_dict[k] = line[v]

        super().__init__(tmp_dict)
        self.__dict__ = self

    def id(self):
        return f"{self.ISRC}{str(datetime.timestamp(self.date))}"

    def as_es_obj(self):
        r = {}
        r['ISRC'] = self.ISRC
        r['artist'] = self.artist
        r['date'] = self.date
        r['list_time'] = self.list_time
        r['hour'] = self.date.hour
        r['day_of_week'] = self.date.isoweekday()
        r['title'] = self.title
        return r

def parse_file(path, tracks, catalog):
    assert isinstance(tracks, list)

    with open(path) as fd:
        rd = csv.DictReader(fd, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in rd:
            track = ListTrack(row)
            tracks.append(track)
            catalog += track

tracks = []
catalog = Catalog()
for path in sys.argv[1:]:
    parse_file(path, tracks, catalog)
es.bulk(tracks)
for track in catalog.search("no eyes"):
    print(track)
