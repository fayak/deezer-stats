#!/usr/bin/env python3

from datetime import datetime
from datetime import timedelta

import json

TITLE=0
ARTIST=1
ISRC=2
ALBUM=3
IP=4
LIST_TIME=5
DATE=8

DATE_FORMAT= "%Y-%m-%d %H:%M:%S.%f"

class Track(dict):
    def __repr__(self):
        return f"{self['nb']} ({self['list_time'] // 60} min) - {self['title']} - {self['artist']}"

def parse_file(path, filter_beg=None):
    with open(path, 'r') as f:
        lines = f.readlines()
    lines = lines[1:]
    tracks = {}
    for line in lines:
        line = line.replace("\n", "")
        line = line.split("\t")
        line[LIST_TIME] = int(line[LIST_TIME])
        if filter_beg is not None and datetime.strptime(line[DATE], "%Y-%m-%d %H:%M:%S.000") < filter_beg:
            continue
        if line[LIST_TIME] < 15:
            continue
        try:
            tracks[line[ISRC]]["nb"] += 1
            tracks[line[ISRC]]["list_time"] += line[LIST_TIME]
            tracks[line[ISRC]]["length"] = max(line[LIST_TIME], tracks[line[ISRC]]["length"])
            tracks[line[ISRC]]["hist"].append(line[LIST_TIME])
            tracks[line[ISRC]]["hist"].sort()
        except:
            track = Track({"title": line[TITLE], "artist": line[ARTIST], "album": line[ALBUM]})
            tracks[line[ISRC]] = track
            tracks[line[ISRC]]["nb"] = 1
            tracks[line[ISRC]]["list_time"] = line[LIST_TIME]
            tracks[line[ISRC]]["length"] = line[LIST_TIME]
            tracks[line[ISRC]]["hist"] = [line[LIST_TIME]]
    return tracks

def filter_date(content, beg=None, end=None):
    if beg is None and end is None:
        return content
    new_content = []
    for track in content:
        listening_time = datetime.strptime(track[DATE], DATE_FORMAT)
        if beg is not None and listening_time < beg:
            continue
        if end is not None and listening_time > end:
            continue
        new_content.append(track)
    return new_content

def top_artist(tracks, n=30):
    artists = {}
    for ISRN, track in tracks.items():
        if track["artist"] not in artists:
            artists[track["artist"]] = track["nb"]
        else:
            artists[track["artist"]] += track["nb"]
    for w,_ in zip(sorted(artists, key=artists.get, reverse=True), range(n)):
        print(f"{artists[w]} - {w}")

def top_track(tracks, n=10):
    for item,_ in zip(sorted(tracks.items(), key=lambda item: item[1]["list_time"] / item[1]["hist"][int((len(item[1]["hist"])/16) * 15)] if len(item[1]["hist"]) > 25 else 0 , reverse=True), range(n)):
        print(item[1])
        #print(f'{item[1]["list_time"]=} / {item[1]["hist"][len(item[1]["hist"])//2]=}')
        #print(item[1]["hist"])

content = parse_file("history.tsv", datetime.strptime("2020-01-01 00:00:00.000", "%Y-%m-%d %H:%M:%S.000"))
top_artist(content, 50)
print("-"*30)
top_track(content, 500)
s = 0
for k, v in content.items():
    s += v['list_time']
print(s)
print("\n")
