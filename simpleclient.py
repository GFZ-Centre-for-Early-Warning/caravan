import time
import bson
import requests

class HMB(object):
    def __init__(self, url, param={}, log_fn=print, retry_wait=10, **kwargs):
        self.__url = url
        self.__param = param
        self.__log_fn = log_fn
        self.__retry_wait = retry_wait
        self.__kwargs = kwargs
        self.__sid = None
        self.__oid = ''
        self.realtime = False

        if 'queue' in self.__param:
            # make sure that ANNOUNCEMENT is subscribed to
            self.__param['queue']['ANNOUNCEMENT'] = { 'seq': -1 }

            # initially set 'keep' to false to get pending data
            for q in self.__param['queue'].values():
                q['keep'] = False

    def __open(self):
        fail = False

        while True:
            try:
                r = requests.post(self.__url + '/open', data=bson.BSON.encode(self.__param), **self.__kwargs)

                if r.status_code == 400:
                    raise requests.exceptions.RequestException("bad request: " + r.text)

                r.raise_for_status()

                ack = bson.BSON(r.content).decode()
                self.__sid = ack['sid']
                self.__oid = ''
                self.__param['cid'] = ack['cid']
                self.__log_fn("session opened, sid={}, cid={}".format(ack['sid'], ack['cid']))

                return

            except requests.exceptions.RequestException as e:
                if not fail:
                    self.__log_fn("error: " + str(e))
                    self.__log_fn("connection to message bus failed, retrying in {} seconds".format(self.__retry_wait))
                    fail = True

                time.sleep(self.__retry_wait)

    def send(self, objlist):
        while True:
            if self.__sid is None:
                self.__open()

            try:
                r = requests.post(self.__url + '/send/' + self.__sid,
                        data=b''.join((bson.BSON.encode(obj) for obj in objlist)),
                        **self.__kwargs)

                if r.status_code == 400:
                    raise requests.exceptions.RequestException("bad request: " + r.text)

                r.raise_for_status()

                return

            except requests.exceptions.RequestException as e:
                self.__log_fn("error: " + str(e))

            self.__sid = None
            self.__log_fn("connection to message bus lost, retrying in {} seconds".format(self.__retry_wait))
            time.sleep(self.__retry_wait)

    def recv(self):
        while True:
            if self.__sid is None:
                self.__open()

            try:
                r = requests.get(self.__url + '/recv/' + self.__sid + self.__oid, **self.__kwargs)

                if r.status_code == 400:
                    raise requests.exceptions.RequestException("bad request: " + r.text)

                r.raise_for_status()

                objlist =  bson.decode_all(r.content)

                for obj in objlist:
                    try:
                        if obj['type'] == 'NEW_QUEUE':
                            if obj['data']['name'] in self.__param['queue']:
                                self.__sid = None

                        elif obj['type'] == 'EOF':
                            self.realtime = True
                            self.__sid = None

                            for q in self.__param['queue'].values():
                                q['keep'] = True

                    except KeyError:
                        pass

                    try:
                        self.__param['queue'][obj['queue']]['seq'] = obj['seq'] + 1
                        self.__oid = '/{}/{}'.format(obj['queue'], obj['seq'])

                    except KeyError:
                        pass

                return objlist

            except bson.errors.BSONError as e:
                self.__log_fn("invalid data received: " + str(e))

            except requests.exceptions.RequestException as e:
                self.__log_fn("error: " + str(e))

            self.__sid = None
            self.__log_fn("connection to message bus lost, retrying in {} seconds".format(self.__retry_wait))
            time.sleep(self.__retry_wait)

