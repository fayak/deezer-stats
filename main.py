#!/usr/bin/env python3

import json
from datetime import datetime
from datetime import timedelta
import csv
import sys
import argparse
import utils

args = {}

class ListTrack(dict):
    def __repr__(self):
        return f"[{self.date}] {str(timedelta(seconds=self.list_time))} - {self['title']} - {self['artist']}"

    def __init__(self, line):
        associations = {
                "title": "Song Title",
                "artist": "Artist",
                "ISRC": "ISRC",
                "album": "Album Title",
                "IP": "IP Address",
                "list_time": "Listening Time",
                "date": "Date",
        }
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

    def is_valid(self):
        global args
        return utils.validation_algorithms[args.valid_algo](self)

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

class Track(dict):
    def __repr__(self):
        return f"{self['title']} - {self['artist']}"

    def __init__(self, track):
        track_obj_attr = ["ISRC", "artist", "title", "album"]
        track_obj = {k: track[k] for k in track_obj_attr}
        super().__init__({**track_obj, "nb": 0, "list_time_sum": 0})
        self.__dict__ = self
        self.dates = []
        self += track

    def __add__(self, other):
        self.nb += 1
        self.list_time_sum += other.list_time
        self.dates.append(other.date)
        return self

    def __eq__(self, other):
        return self.ISRC == other.ISRC

class Catalog():
    def __init__(self, tracks=None):
        self.tracks = {}
        if tracks is not None:
            for track in tracks:
                self += track

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

def parse_file(path, tracks, catalog):
    assert isinstance(tracks, list)

    with open(path) as fd:
        rd = csv.DictReader(fd, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in rd:
            track = ListTrack(row)
            tracks.append(track)
            catalog += track

def config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--es", type=str, default="false", choices=["true", "false"])
    parser.add_argument("--valid-algo", type=str, default="min_10", choices=utils.validation_algorithms.keys(), help="Defines what algorithm to use to know if a track was really listened to or not")

    actions = parser.add_argument_group('Actions')
    actions.add_argument("--top-track", action="store_true", default=False, help="List the top tracks")
    actions.add_argument("--top-track-by-time", action="store_true", default=False, help="List the top tracks by listening time")
    actions.add_argument("--top", type=int, default=25, help="The top size")
    actions.add_argument("--min", type=int, default=None, help="All songs listened minimun x times")
    actions.add_argument("--forgotten-hits", action="store_true", default=False)
    actions.add_argument("--forgotten-hits-start", type=datetime.fromisoformat, default=None)
    actions.add_argument("--forgotten-hits-end", type=datetime.fromisoformat, default=None)
    actions.add_argument("--forgotten-hits-top", type=int, default=100)
    actions.add_argument("--forgotten-hits-bucket-size", type=int, default=3)

    filters = parser.add_argument_group('Filters')
    filters.add_argument("--date-before", type=datetime.fromisoformat, default=None, help="Filter out tracks listened after this date")
    filters.add_argument("--date-after", type=datetime.fromisoformat, default=None, help="Filter out tracks listened before this date")

    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    assert args.valid_algo in utils.validation_algorithms
    actions = ["top_track", "top_track_by_time", "min", "forgotten_hits"]
    filters = ["date_before", "date_after"]

    args.actions = []
    for action in actions:
        if getattr(args, action) is not None and getattr(args, action):
            args.actions.append(action)
    args.filters = []
    for filter in filters:
        if getattr(args, filter) is not None:
            args.filters.append(filter)
    return args

def main():
    global args
    args = config()

    tracks = []
    catalog = Catalog()
    for path in args.files:
        parse_file(path, tracks, catalog)

    if len(args.actions) > 0:
        sub_tracks = [x for x in tracks if x.is_valid()]

        for filter in args.filters:
            sub_tracks = getattr(utils, filter)(sub_tracks, args=args)

        sub_catalog = Catalog(sub_tracks)

    for action in args.actions:
        getattr(utils, action)(sub_tracks, sub_catalog, args)

    if args.es == "true":
        import es
        es.reset_index()
        es.bulk(tracks)

if __name__ == "__main__":
    main()
