#!/usr/bin/python

import requests
import jsontree
import json


class fetcher:
    def __init__(self, url, alias=None):
        self.r = requests.get(url)
        self.plainjson = self.r.content
        self.data = jsontree.loads(self.plainjson)
        self.name = alias

class storrage(object):
    d = []
    urls = {}
    def __init__(self,urls_):
        self.urls = urls_
        self.loadfiles()
     
    def loadfiles(self):
        self.d = []
#        print ('fetching data')
        for alias,url in self.urls.iteritems():
            self.d.append(fetcher(url, alias))

    def dump_all_json(self):
        result = '{'
        count = len(self.d)
        for i in self.d:
            count -= 1
            result = result + '"'+ i.name + '" : ' + i.plainjson
            if count > 0:
                result += ','
        result += '}'
        return result

    def get_all_json(self):
        data = self.get_all()
        return json.dumps(data)
