from __future__ import print_function
import pygatt
import struct
import logging
from ConfigParser import SafeConfigParser
import time
import os

# Setting up logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Read configuration from ini file
config = SafeConfigParser()
config.read('config.ini')

# Set up BLE adapter
adapter = pygatt.backends.BGAPIBackend()

# Device characteristics
Char_glucose = "00002a18-0000-1000-8000-00805f9b34fb"

# Wait for the device to be ready
def wait_for_device(device_name):
    while True:
        try:
            adapter.start()
            device = adapter.connect(config.get('GLUCOSE', 'ble_address'))
            log.debug("Device %s is ready" % device_name)
            return device
        except pygatt.exceptions.NotConnectedError:
            log.debug("Waiting for device %s to be ready" % device_name)
            time.sleep(1)
        finally:
            adapter.stop()

# Connect to the device
def connect_device(ble_address):
    try:
        device = adapter.connect(ble_address)
        log.debug("Device connected")
        return device
    except pygatt.exceptions.NotConnectedError:
        log.debug("Could not connect to device")
        return None

# Process the glucose reading received
def processIndication(handle, value):
    glucose = struct.unpack('h', value)[0]/18.0
    log.debug("Latest glucose reading: %s" % glucose)
    return glucose

while True:
    device = connect_device(config.get('GLUCOSE', 'ble_address'))
    if device:
        glucose = []
        handle_glucose = device.get_handle(Char_glucose)
        continue_comms = True
        try:
            device.subscribe(Char_glucose,
                             callback=processIndication,
                             indication=True)
        except pygatt.exceptions.NotConnectedError:
            continue_comms = False
        if continue_comms:
            log.debug('Waiting for notifications for another 30 seconds')
            time.sleep(30)
            try:
                device.disconnect()
            except pygatt.exceptions.NotConnectedError:
                log.debug('Could not disconnect...')
            log.debug('Done receiving glucose data')
            if glucose:
                glucose_sorted = sorted(glucose, key=lambda k: k['timestamp'], reverse=True)
                latest_glucose = glucose_sorted[0]
                log.debug("Latest glucose reading: %s" % latest_glucose)
            else:
                log.error('No glucose data received')
