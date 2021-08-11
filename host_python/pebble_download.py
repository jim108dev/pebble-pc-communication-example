#!/usr/bin/env python

"""
 Receive messages from pebble via Data-Logging.
"""

import csv
import logging
import struct
import uuid

from libpebble2.services.data_logging import DataLoggingService

from pebble_communication import (CommunicationKeeper,
                                  PebbleConnectionException, get_conf,
                                  open_connection)

logging.basicConfig(level=logging.DEBUG)

def main(conf):

    pebble = open_connection(conf)

    # Register service for app messages
    appservice = DataLoggingService(pebble)

    commwatch = CommunicationKeeper(conf, appservice)
    appservice.register_handler("nack", commwatch.nack_received)
    appservice.register_handler("ack", commwatch.ack_received)

    sessions = appservice.list()

    logging.debug("Found sessions:")
    logging.debug(sessions)

    session_ids = [s['session_id'] for s in sessions if s['app_uuid']
                   == uuid.UUID(conf.uuid) and s['log_tag'] == conf.download_log_tag]

    if (len(session_ids) == 0):
        logging.debug("dataset not found")
        return

    records = []
    for session_id in session_ids:
        logging.debug("Downloading session (%d)" % session_id)

        data = appservice.download(session_id)
        # (DataLoggingDespoolOpenSession, bytearray)
        logging.debug(data)
        (_, byte_values) = data
        for r in bytes_to_records(byte_values, conf.download_record_size, conf.download_record_fmt):
            records.append(r)

    append_to_file(records, conf.download_filename, conf.download_header)

    logging.debug("%d records written" % len(records))


def bytes_to_records(byte_values, record_size, fmt):
    total = len(byte_values)
    logging.debug("Convert %d bytes to records of size %d" % (total, record_size))
    for offset in xrange(0,total, record_size):
        record = struct.unpack_from(fmt, byte_values,offset=offset)
        yield record

def append_to_file(records, filename, header):
    if not records:
        return

    f = open(filename, "wb")
    cr = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONE,
                    skipinitialspace=True)
    cr.writerow(header)
    for record in records:
        cr.writerow(record)
    f.close()


if __name__ == "__main__":
    try:
        main(get_conf())
    except PebbleConnectionException as error:
        logging.error("PebbleConnectionException: " + str(error))
        logging.error("Bailing out!")
