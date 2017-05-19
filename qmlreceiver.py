#!/usr/bin/env python3

import sys
import zlib
from optparse import OptionParser
from simpleclient import HMB

VERSION = "0.1 (2015.288)"

RETRY_WAIT = 10

def handleEvent(gdacs, data):
    print("{dateTime} M={magnitude} {location} -> {eventID}.xml".format(**gdacs))

    with open(gdacs['eventID'] + '.xml', 'wb') as f:
        f.write(zlib.decompress(data))

def worker(source):
    while True:
        for obj in source.recv():
            try:
                if obj['type'] == 'QUAKEML':
                    handleEvent(obj['gdacs'], obj['data'])

                elif obj['type'] == 'EOF':
                    print("Waiting for next events in real time")

            except (KeyError, TypeError) as e:
                print("invalid data received: " + str(e))

def main():
    parser = OptionParser(usage="usage: %prog [options]", version="%prog v" + VERSION)
    parser.set_defaults(timeout = 120, backfill = 10)

    parser.add_option("-u", "--user", type="string", dest="user",
        help="Source HMB username")

    parser.add_option("-p", "--password", type="string", dest="password",
        help="Source HMB password")

    parser.add_option("-s", "--source", type="string", dest="source",
        help="Source HMB URL")

    parser.add_option("-t", "--timeout", type="int", dest="timeout",
        help="Timeout in seconds (default %default)")

    parser.add_option("-b", "--backfill", type="int", dest="backfill",
        help="Number of messages to backfill (default %default)")

    (opt, args) = parser.parse_args()

    if args:
        parser.error("incorrect number of arguments")

    if opt.source is None:
        parser.error("missing source HMB")

    param = {
        'heartbeat': opt.timeout//2,
        'queue': {
            'QUAKEML': {
                'seq': -opt.backfill-1
            }
        }
    }

    auth = (opt.user, opt.password) if opt.user and opt.password else None

    source = HMB(opt.source, param, retry_wait=RETRY_WAIT,
            timeout=opt.timeout, auth=auth, verify=False)

    print("Retrieving past {} events".format(opt.backfill))

    worker(source)

if __name__ == "__main__":
    main()

