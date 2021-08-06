#!/usr/bin/env python

"""
 Simple looper to receive messages from pebble.
 Modified from https://github.com/susundberg/pebble-linux-remote 
 original author: Pauli Salmenrinne (License  GPL-2.0)
"""

import csv
import logging
import time
import uuid

from libpebble2.protocol.apps import AppRunState, AppRunStateStart
from libpebble2.services.appmessage import AppMessageService, CString, Uint8

from pebble_comm import (CommunicationKeeper, PebbleConnectionException,
                         get_settings, open_connection)

logging.basicConfig(level=logging.DEBUG)


class PebbleConnectionException(Exception):
    pass


logging.basicConfig(level=logging.DEBUG)


def read_data():
    with open('data/upload.csv', 'r') as file:
        reader = csv.reader(file, delimiter=';', quoting=csv.QUOTE_NONE,
                            skipinitialspace=True)
        next(reader, None) #header row
        return [';'.join(cols) for cols in reader]


COMMUNICATION_KEY_MAX = 100
COMMUNICATION_KEY_DATA = 200


def main(settings):
    data = read_data()

    pebble = open_connection(settings)

    # Register service for app messages
    appservice = AppMessageService(pebble)

    commwatch = CommunicationKeeper(settings, appservice)
    appservice.register_handler("nack", commwatch.nack_received)
    appservice.register_handler("ack", commwatch.ack_received)

    # Start the watchapp
    logging.debug("Send uuid=%s", settings.uuid)
    pebble.send_packet(AppRunState(
        command=0x01, data=AppRunStateStart(uuid=uuid.UUID(settings.uuid))))

    commwatch.send_message({COMMUNICATION_KEY_MAX: Uint8(len(data))})

    for row in data:
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
        main(get_settings())
    except PebbleConnectionException as error:
        logging.error("PebbleConnectionException: " + str(error))
        logging.error("Bailing out!")
