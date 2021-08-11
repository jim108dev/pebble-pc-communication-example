#!/usr/bin/env python

"""
 Simple looper to send messages to pebble.
 Modified from https://github.com/susundberg/pebble-linux-remote.
 Original author: Pauli Salmenrinne (License  GPL-2.0)
"""

import csv
import logging
import time
import uuid

from libpebble2.protocol.apps import AppRunState, AppRunStateStart
from libpebble2.services.appmessage import AppMessageService, CString, Uint8

from pebble_communication import (CommunicationKeeper,
                                  PebbleConnectionException, get_conf,
                                  open_connection)

logging.basicConfig(level=logging.DEBUG)


class PebbleConnectionException(Exception):
    pass


def read_data(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter=';', quoting=csv.QUOTE_NONE,
                            skipinitialspace=True)
        next(reader, None) #header row
        return [';'.join(cols) for cols in reader]


MAX_ROW_LEN = 255
COMMUNICATION_KEY_MAX = 100
COMMUNICATION_KEY_DATA = 200


def main(conf):
    data = read_data(conf.upload_filename)

    pebble = open_connection(conf)

    # Register service for app messages
    appservice = AppMessageService(pebble)

    commwatch = CommunicationKeeper(conf, appservice)
    appservice.register_handler("nack", commwatch.nack_received)
    appservice.register_handler("ack", commwatch.ack_received)

    # Start the watchapp
    logging.debug("Send uuid=%s", conf.uuid)
    pebble.send_packet(AppRunState(
        command=0x01, data=AppRunStateStart(uuid=uuid.UUID(conf.uuid))))

    commwatch.send_message({COMMUNICATION_KEY_MAX: Uint8(len(data))})

    for row in data:
        if len(row) > MAX_ROW_LEN:
            logging.warn("Entry is longer than %d, ignoring '%s'" % (MAX_ROW_LEN, row))
            continue
        commwatch.send_message({COMMUNICATION_KEY_DATA: CString(row)})

    # Wait for all
    for loop in range(10):
        if len(commwatch.pending) == 0:
            break
        if commwatch.error:
            raise PebbleConnectionException("Commwatch:" + commwatch.error)
        time.sleep(0.1)
    else:
        raise PebbleConnectionException("Pebble not respoding")

    logging.info("Connection ok")


if __name__ == "__main__":
    try:
        main(get_conf())
    except PebbleConnectionException as error:
        logging.error("PebbleConnectionException: " + str(error))
        logging.error("Bailing out!")
