from main import es


def search_for_all_docs():
  allDocs = es.search(index="amazon", body={
    "size": 10000,
    "query": {
      "match_all": {}
    }
  })
  return allDocs


def search_for_some_docs():
  some_docs = es.search(index="amazon", body={
    "query": {
      "match": {
        "avgRating": 5
      }
    },
    "size": 10
  })
  return some_docs
