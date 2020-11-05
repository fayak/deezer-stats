#!/usr/bin/env python3

from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta

# VALIDATION ALGORITHMS

def va_min_10(list_track):
    return list_track.list_time > 10

def va_all(list_track):
    return True


validation_algorithms = {
    "min_10": va_min_10,
    "all": va_all,
    }

# FILTERS
def _date(tracks, method, **kwargs):
    def _worker(tracks, method, date):
        r = []
        for track in tracks:
            if getattr(track.date, method)(date):
                r.append(track)
        return r

    if (date := kwargs.get("date", None)) is not None:
        return _worker(tracks, method, date)
    elif method == "__gt__":
        return _worker(tracks, method, kwargs['args'].date_after)
    else:
        return _worker(tracks, method, kwargs['args'].date_before)

def date_after(tracks, *args, **kwargs):
    return _date(tracks, "__gt__", **kwargs)

def date_before(tracks, *args, **kwargs):
    return _date(tracks, "__lt__", **kwargs)

# ACTIONS

def print_tracks(tracks, title, top):
    print(title)
    for item,_ in zip(tracks, range(1, top + 1)):
        print(f"[{_:4}] {item[1].nb:3} ({str(timedelta(seconds=item[1].list_time_sum))}): {item[1]}")

def _top_tracks(tracks, catalog):
    sorted_tracks = sorted(catalog.tracks.items(), key=lambda item: item[1].nb, reverse=True)
    return sorted_tracks

def top_track(tracks, catalog, args):
    sorted_tracks = _top_tracks(tracks, catalog)
    print_tracks(sorted_tracks, "Top most listened track", args.top)

def top_track_by_time(tracks, catalog, args):
    sorted_tracks = sorted(catalog.tracks.items(), key=lambda item: item[1].list_time_sum, reverse=True)
    print_tracks(sorted_tracks, "Top most listened track by listening-time", args.top)

def min(tracks, catalog, args):
    sorted_tracks = sorted(catalog.tracks.items(), key=lambda item: item[1].nb, reverse=True)
    i = 1
    print(f"Top tracks listened minimum {args.min} times")
    for iscr, track in sorted_tracks:
        if track.nb >= args.min:
            print(f"[{i:4}] {track.nb:3} ({str(timedelta(seconds=track.list_time_sum))}): {track}")
            i += 1
        else:
            break

def forgotten_hits(tracks, catalog, args):
    from main import Catalog

    date = datetime.now()
    if args.forgotten_hits_start is None:
        start_date = date - relativedelta(years=1)
    else:
        start_date = args.forgotten_hits_start
    if args.forgotten_hits_end is None:
        end_date = date
    else:
        end_date = args.forgotten_hits_end

    top_ref = [k for k, v in _top_tracks(tracks, catalog)[:args.forgotten_hits_top]]

    forgotten_hits = []
    forgotten_hits_meta = []

    while start_date < end_date:
        bucket = date_after(date_before(tracks, date=(start_date + relativedelta(months=1))), date=start_date)
        bucket_catalog = Catalog(bucket)
        sorted_bucket = _top_tracks(bucket, bucket_catalog)
        i = 0
        for k, track in sorted_bucket:
            if k in top_ref or k in forgotten_hits_meta:
                continue
            forgotten_hits.append((start_date, track))
            forgotten_hits_meta.append(k)
            i += 1
            if i == args.forgotten_hits_bucket_size:
                break

        start_date += relativedelta(months=+1)
    for date, track in forgotten_hits:
        print(f"{date.date()} {track.nb:3} ({str(timedelta(seconds=track.list_time_sum))}): {track}")
