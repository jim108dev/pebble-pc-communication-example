import argparse
import logging
import uuid

import ConfigParser
import libpebble2.exceptions
from libpebble2.communication import PebbleConnection
from libpebble2.communication.transports.serial import SerialTransport
from libpebble2.communication.transports.websocket import WebsocketTransport


class PebbleConnectionException(Exception):
    pass


def get_settings():
    parser = argparse.ArgumentParser(
        description='Pebble to linux keyboard bridge')
    parser.add_argument("config", help="Set the configuration file")
    settings = parser.parse_args()

    conf = ConfigParser.ConfigParser()
    conf.read(settings.config)

    settings.transport = conf.get('main', 'transport')
    settings.device = conf.get('main', 'device')
    settings.uuid = conf.get('main', 'uuid')

    settings.key_mappings = {}
    return settings


class CommandHandler:
    """ Class for handling the incoming app-messages - commands - from the pebble """

    def __init__(self, settings):
        self.settings = settings

    def message_received_event(self, transaction_id, uuid, data):
        logging.debug("Message received! uuid=%s, data=%s" % (uuid, data))


class CommunicationKeeper:
    """ Class for handling re-sending of NACK-ed messages """
    NACK_COUNT_LIMIT = 5

    def __init__(self, settings, appservice):
        self.settings = settings
        logging.debug("Settings: uuid=(%s)" % settings.uuid)
        self.uuid = uuid.UUID(settings.uuid)

        self.pending = {}
        self.nack_count = 0
        self.appservice = appservice
        self.error = None

    def check_uuid(self, uuid):
        if uuid != self.uuid:
            logging.debug("Ignoring appdata from unknown sender (%s)" % uuid)
            return False
        return True

    def nack_received(self, transaction_id, uuid):
        """ Callback functions for the library call when receiving nack """
        logging.warning(
            "NACK received transaction_id=(%s), uuid=(%s)" % (transaction_id, uuid))
        if self.check_uuid(uuid) == False:
            return
        if transaction_id not in self.pending:
            raise PebbleConnectionException("Invalid transaction ID received")

        # We got nack from the watch
        logging.warning("NACK received for packet!")
        self.nack_count += 1
        if self.nack_count > self.NACK_COUNT_LIMIT:
            # we are inside the receive thread here, exception will kill only
            # that
            self.error = "Nack count limit reached, something is wrong."
            return
        # self.send_message( self.pending[transaction_id] )
        del self.pending[transaction_id]

    def ack_received(self, transaction_id, uuid):
        logging.debug("ACK received for packet!")
        if self.check_uuid(uuid) == False:
            return
        if transaction_id not in self.pending:
            raise Exception("Invalid transaction ID received")
        del self.pending[transaction_id]

    def send_message(self, data):
        """ Send message and retry sending if it gets nacked """
        transaction_id = self.appservice.send_message(self.uuid, data)
        self.pending[transaction_id] = data


def open_connection(settings):
    if settings.transport == "websocket":
        pebble = PebbleConnection(WebsocketTransport(
            settings.device), log_packet_level=logging.DEBUG)
    else:  # No elif, for compatibility with older configs
        pebble = PebbleConnection(SerialTransport(
            settings.device), log_packet_level=logging.DEBUG)
    pebble.connect()

    # For some reason it seems to timeout for the first time, with "somebody is eating our input" error,
    # replying seems to help.
    for loop in range(5):
        try:
            pebble.run_async()
            break
        except libpebble2.exceptions.TimeoutError:
            logging.info("Pebble timeouted, retrying..")
            continue
    return pebble
