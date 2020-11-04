#!/usr/bin/env python3

from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch()

mapping = {
    "mappings": {
        "properties": {
          "ISRC": {
              "type": "keyword"
            },
          "artist": {
            "type": "keyword"
          },
          "date": {
            "type": "date",
            "format": "yyyy-MM-ddTHH:mm:ss"
          },
          "list_time": {
            "type": "integer"
          },
          "hour": {
            "type": "integer"
          },
          "day_of_week": {
            "type": "integer"
          },
          "title": {
            "type": "keyword"
          }
        }
    }
}

def reset_index():
    es.indices.delete(index='deezer', ignore=[404])
    es.indices.create(index='deezer', ignore=[400], body=mapping)

def bulk(tracks):
    actions = [
          {
            "_index": "deezer",
            "_id": track.id(),
            "_source": track.as_es_obj()
            }
          for track in tracks
        ]
    helpers.bulk(actions=actions, client=es)
