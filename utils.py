#!/usr/bin/env python3


# VALIDATION ALGORITHMS

def va_min_10(list_track):
    return list_track.list_time > 10

def va_all(list_track):
    return True


validation_algorithms = {
    "min_10": va_min_10,
    "all": va_all,
    }

# ACTIONS

def top_track(tracks, catalog):
    sorted_tracks = sorted(catalog.tracks.items(), key=lambda item: item[1].nb, reverse=True)
    for item,_ in zip(sorted_tracks, range(50)):
        print(item[1])
