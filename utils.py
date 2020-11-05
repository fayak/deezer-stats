#!/usr/bin/env python3

from datetime import timedelta

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

def print_tracks(tracks, title, args):
    print(title)
    for item,_ in zip(tracks, range(1, args.top + 1)):
        print(f"[{_:02}] {item[1].nb} ({str(timedelta(seconds=item[1].list_time_sum))}): {item[1]}")

def top_track(tracks, catalog, args):
    sorted_tracks = sorted(catalog.tracks.items(), key=lambda item: item[1].nb, reverse=True)
    print_tracks(sorted_tracks, "Top most listened track", args)

def top_track_by_time(tracks, catalog, args):
    sorted_tracks = sorted(catalog.tracks.items(), key=lambda item: item[1].list_time_sum, reverse=True)
    print_tracks(sorted_tracks, "Top most listened track by listening-time", args)

def min(tracks, catalog, args):
    sorted_tracks = sorted(catalog.tracks.items(), key=lambda item: item[1].nb, reverse=True)
    i = 1
    for iscr, track in sorted_tracks:
        if track.nb >= args.min:
            print(f"[{i:02}] {track.nb} ({str(timedelta(seconds=track.list_time_sum))}): {track}")
            i += 1
        else:
            break
