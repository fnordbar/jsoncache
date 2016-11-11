from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from threading import Thread
import threading
import time
import mmap
import contextlib
import os
import sys
import json
import hashlib


from fetch import fetcher, storrage



SERVER_ADDRESS = (HOST, PORT) = '', 8888


TIMEOUT = 5
STATUSFILE = '/tmp/status'
STATUSTIME = '/tmp/statustime'

JSON_SOURCE = {
    'dummy':    'https://www.googleapis.com/customsearch/v1',
}

def updater():
    shutdown = None
    while not shutdown:
        data = storrage(JSON_SOURCE)
        with open(STATUSTIME, 'r+b') as f:
            try:
                now = str(int(time.time()))
                mm = mmap.mmap(f.fileno(), 0, flags=mmap.MAP_SHARED, access=mmap.PROT_WRITE)
                mm.seek(0)
                mm.resize(len(now))
                mm.write(now)
                #print('new time set')
                mm.flush
                mm.close
                f.flush
                f.close
            except ValueError as e:
                print(e.message + 'failed to set new timestamp')

        with open(STATUSFILE, 'r+b') as st:
            try:
                jsondata = data.dump_all_json()
                mm = mmap.mmap(st.fileno(), 0, flags=mmap.MAP_SHARED, access=mmap.PROT_WRITE)
                mm.seek(0)
                mm.resize(len(jsondata))
                mm.write(jsondata)
                #print('status updated ' + hashlib.sha1(jsondata).hexdigest())
                mm.flush
                mm.close
                st.flush
                st.close
            except ValueError as e:
                print(e.message + 'failed to set new status')
        time.sleep(TIMEOUT)

class Handler(BaseHTTPRequestHandler):
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()


        return
    def do_GET(self):

        """ try n times to read """
        for i in range(0,5):
            """ gather status update time"""
            f = open(STATUSTIME, "rb")
            try:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                last = int(mm.readline())
                mm.seek(0)
                mm.close()
            except ValueError as e:
                print(e.message + str(i) + ' failed to read status time')
                continue
            f.close()
            """ gather json status """
            st = open(STATUSFILE, "rb")
            try:
                buf = mmap.mmap(st.fileno(), 0, access=mmap.ACCESS_READ)
                raw = (buf.read(len(buf)))
                #print('reading status ' + hashlib.sha1(raw).hexdigest())
            except ValueError as e:
                print(e.message + str(i) + ' failed to read json status')
                continue
            data = None
            if raw is not None:
                try:
                    data = raw
                    #data = json.loads(raw)
                except ValueError as e:
                    print(e.message + str(i) + ' failed to load json status')
                    continue
            """ all done - exit for loop"""
            break
        else:
            print('all attempts failed')
            self.send_response(500)
            self.end_headers()
            self.wfile.write('\n')
            return
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
#        message = threading.currentThread().getName() + ' ' + str(last) + ' ' +str(data)
#        message = str(raw)
        message = str(data)
        
        self.wfile.write(message)
        self.wfile.write('\n')
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


if __name__ == '__main__':
    for f in (STATUSTIME, STATUSFILE):
#        print(f)
        fd = os.open(f, os.O_CREAT | os.O_TRUNC | os.O_RDWR)
        assert os.write(fd, '\x00' * mmap.PAGESIZE) == mmap.PAGESIZE
    # write a simple example file
    t = Thread(target=updater)
    t.daemon = True
    t.start()
    time.sleep(10)
    server = ThreadedHTTPServer(SERVER_ADDRESS, Handler)
    print 'Starting server '+ str(SERVER_ADDRESS) +', use <Ctrl-C> to stop'

    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print('shuting down')
        sys.exit()
