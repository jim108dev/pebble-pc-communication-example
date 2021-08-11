#!/usr/bin/env python

"""
 Helper classes to establish a connection to pebble.
 Modified from https://github.com/susundberg/pebble-linux-remote.
 Original author: Pauli Salmenrinne (License  GPL-2.0)
"""

import argparse
import json
import logging
import os
import sys
import tempfile
import uuid

import ConfigParser
import libpebble2.exceptions
from libpebble2.communication import PebbleConnection
from libpebble2.communication.transports.serial import SerialTransport
from libpebble2.communication.transports.websocket import WebsocketTransport


class PebbleConnectionException(Exception):
    pass


def get_conf():
    parser = argparse.ArgumentParser(
        description='Pebble to linux keyboard bridge')
    parser.add_argument("config", help="Set the configuration file")
    conf = parser.parse_args()

    parser = ConfigParser.ConfigParser()
    parser.read(conf.config)

    conf.transport = parser.get('main', 'transport')
    conf.device = parser.get('main', 'device')
    conf.uuid = parser.get('main', 'uuid')

    conf.upload_filename = parser.get('upload', 'filename')

    conf.download_filename = parser.get('download', 'filename')
    conf.download_record_fmt = parser.get('download', 'record_fmt')
    conf.download_record_size = parser.getint('download', 'record_size')
    conf.download_header = parser.get('download', 'header').strip('"').split(';')
    conf.download_log_tag = parser.getint('download', 'log_tag')

    conf.key_mappings = {}
    return conf


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
        device = get_emulator_url(settings.device) if settings.device == "aplite" else settings.device
        print("device = %s" % device)
        pebble = PebbleConnection(WebsocketTransport(device), log_packet_level=logging.DEBUG)
            
    if settings.transport == "bluetooth":
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

def get_emulator_url(device):
    try:
        e = json.load(open(tempfile.gettempdir()+"/pb-emulator.json"))
        emul = e[device]
    except IOError:
        print("FileMsgBridge: Emu file not found (not running)")
        exit()
    except KeyError:
        print("FileMsgBridge: Emu data not found (not running) : " + sys.argv[1])
        exit()

    emuvsn=emul.keys()[0]
    pid=emul[emuvsn]['pypkjs']['pid']
    port=emul[emuvsn]['pypkjs']['port']
    if (not is_process_running(pid)):
        print("FileMsgBridge: Emu process not found (not running) : " + sys.argv[1])
        exit()
    return "ws://localhost:"+str(port)

def is_process_running(process_id):
    try:
        os.kill(process_id, 0)
        return True
    except OSError:
        return False
