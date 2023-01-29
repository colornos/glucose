from __future__ import print_function
import sys
import pygatt.backends
import logging
from ConfigParser import SafeConfigParser
import time
import subprocess
from struct import *
from binascii import hexlify
import os
import threading

import pygatt

class RACPHandler(pygatt.backends.BGAPIBackendDelegate):
    def __init__(self):
        pygatt.backends.BGAPIBackendDelegate.__init__(self)
        self.records = []

    def handleNotification(self, handle, value):
        if handle == 0x2F:
            # Handle glucose measurement notifications
            self.records.append(value)
            print("Received glucose measurement:", value)

class GlucoseMonitor:
    def __init__(self, mac_address):
        self.adapter = pygatt.backends.BGAPIBackend()
        self.adapter.start()
        self.adapter.delegate = RACPHandler()
        self.device = self.adapter.connect(mac_address)
        self.service = self.device.discover_characteristic("00001808-0000-1000-8000-00805f9b34fb")

    def read_all_records(self):
        # Send RACP command [1,1] to read all records
        self.service.write(bytes([1, 1]),True)

    def read_first_record(self):
        # Send RACP command [1,5] to read first record
        self.service.write(bytes([1, 5]),True)

    def read_last_record(self):
        # Send RACP command [1,6] to read last record received
        self.service.write(bytes([1, 6]),True)

    def read_record_from(self, record_num):
        # Send RACP command [1,3,1,record_num,0] to read extract from record record_num onwards
        command = struct.pack("<BBBBB", 1, 3, 1, record_num, 0)
        self.service.write(command,True)

    def num_records(self):
        # Send RACP command [4,1] to get number of records
        self.service.write(bytes([4, 1]),True)

    def subscribe_glucose_measurement(self):
        # Register for glucose measurement notifications
        self.device.subscribe("00002a18-0000-1000-8000-00805f9b34fb",callback=self.handleNotification)

if __name__ == "__main__":
    mac_address = "00:81:F9:B2:24:74" # Replace with the MAC address of your BGM
    monitor = GlucoseMonitor(mac_address)
    monitor.subscribe_glucose_measurement()
    while True:
        monitor.read_last_record()
        time.sleep(1)
