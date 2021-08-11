#!/usr/bin/env python

"""
 Receive messages from pebble via Data-Logging.
"""

import logging

from libpebble2.services.data_logging import DataLoggingService

from pebble_communication import (CommunicationKeeper, PebbleConnectionException,
                         get_conf, open_connection)

logging.basicConfig(level=logging.DEBUG)

def main(conf):

    pebble = open_connection(conf)

    # Register service for app messages
    appservice = DataLoggingService(pebble)

    commwatch = CommunicationKeeper(conf, appservice)
    appservice.register_handler("nack", commwatch.nack_received)
    appservice.register_handler("ack", commwatch.ack_received)

    sessions = appservice.list()

    for s in sessions:
        appservice.download(s['session_id'])

if __name__ == "__main__":
    try:
        main(get_conf())
    except PebbleConnectionException as error:
        logging.error("PebbleConnectionException: " + str(error))
        logging.error("Bailing out!")
