#!/usr/bin/env python3

"""
 Simple looper to receiven and send messages to the pebble.
 author: Pauli Salmenrinne
"""

import csv
import logging
import struct
import uuid

from libpebble2.services.data_logging import DataLoggingService

from pebble_comm import (CommunicationKeeper, PebbleConnectionException,
                         get_settings, open_connection)

logging.basicConfig(level=logging.DEBUG)

DOWNLOAD_COLUMNS = ["id", "last_displayed"]
RECORD_SIZE = 8

def main(settings):
    """ Main function for the communicatior, loops here """

    pebble = open_connection(settings)

    # Register service for app messages
    appservice = DataLoggingService(pebble)

    commwatch = CommunicationKeeper(settings, appservice)
    appservice.register_handler("nack", commwatch.nack_received)
    appservice.register_handler("ack", commwatch.ack_received)

    sessions = appservice.list()

    # sweep
    # for s in sessions:
    #    appservice.download(s['session_id'])

    logging.debug("Found sessions:")
    logging.debug(sessions)

    session_ids = [s['session_id'] for s in sessions if s['app_uuid']
                   == uuid.UUID(settings.uuid) and s['log_tag'] == 1]

    if (len(session_ids) == 0):
        logging.debug("dataset not found")
        return

    records = []
    for session_id in session_ids:
        logging.debug("Downloading session (%d)" % session_id)

        data = appservice.download(session_id)
        logging.debug(data)
        # (DataLoggingDespoolOpenSession, bytearray)
        (session, byte_values) = data
        if not byte_values:
            continue

        records_size = len(byte_values)
        logging.debug("downloaded %d bytes, record size = %d" % (records_size, RECORD_SIZE))
        for offset in xrange(0,records_size,RECORD_SIZE):
            record = struct.unpack_from('>BL', byte_values,offset=offset)
            logging.debug("Downloaded (%d,%ld)" % record)
            records.append(record)

    if len(records) > 0:
        append_to_file(records)


def append_to_file(records):
    f = open("data/download.csv", "wb")
    cr = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE,
                    skipinitialspace=True)
    cr.writerow(DOWNLOAD_COLUMNS)
    for record in records:
        cr.writerow(record)
        logging.debug("Wrote (%d,%ld) to csv" % record)
    f.close()


if __name__ == "__main__":
    try:
        main(get_settings())
    except PebbleConnectionException as error:
        logging.error("PebbleConnectionException: " + str(error))
        logging.error("Bailing out!")
