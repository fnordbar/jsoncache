jsoncache
=========

* start.sh activate the python virtualenv and starts the webserver/fetcher process
* copy init Script into /etc/init.d and link as nessesary (eg rc2.d, rc0.d, rc6.d)

Dependencies:
    * virtualenv
    * python json tree



fetches json files from:
```
    JSON_SOURCE = {
        'dummy':    'https://www.googleapis.com/customsearch/v1',
    }
```

stores merged files and timestamp in temporary files:
```
    STATUSFILE = '/tmp/status'
    STATUSTIME = '/tmp/statustime'
```

