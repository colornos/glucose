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
import thread

# RACP commands
RACP_COMMAND_REPORT_STORED_RECORDS = [1,1]
RACP_COMMAND_REPORT_NUMBER_OF_STORED_RECORDS = [4,1]
RACP_COMMAND_DELETE_STORED_RECORDS = [3,1]
RACP_COMMAND_ABORT_OPERATION = [0,0]
RACP_COMMAND_REPORT_LAST_STORED_RECORD = [1,6]
RACP_COMMAND_REPORT_FIRST_STORED_RECORD = [1,5]

# RACP response codes
RACP_RESPONSE_SUCCESS = [1]
RACP_RESPONSE_NO_RECORDS_FOUND = [2]
RACP_RESPONSE_OP_CODE_NOT_SUPPORTED = [3]
RACP_RESPONSE_INVALID_OPERATOR = [4]
RACP_RESPONSE_OPERATOR_NOT_SUPPORTED = [5]
RACP_RESPONSE_INVALID_OPERAND = [6]
RACP_RESPONSE_NO_COMMAND_IN_PROGRESS = [7]
RACP_RESPONSE_ABORT_UNSUCCESSFUL = [8]

# Interesting characteristics
RACP_UUID = '00002a52-0000-1000-8000-00805f9b34fb'  # RACP

glucose_data = []

# BLE adapter setup
adapter = pygatt.GATTToolBackend()
adapter.start()
addresstype = pygatt.BLEAddressType.random

# Connect to device
address = "XX:XX:XX:XX:XX:XX"  # replace with actual device address
device = adapter.connect(address, address_type=addresstype)

def processIndication(handle, value):
    """
    Indication handler:
    Receives indication and stores values into result Dict
    (see decode functions for Dict definition)
    handle: byte
    value: bytearray
    """
    if handle == RACP_UUID:
        glucose_data.append(value)

# Enable notifications for RACP
device.subscribe(RACP_UUID, callback=processIndication)

# Send RACP command to read last glucose record received
device.char_write(RACP_UUID, bytearray(RACP_COMMAND_REPORT_LAST_STORED_RECORD))

# Wait for data
while True:
    if glucose_data:
        print(glucose_data[-1])
        break
    time.sleep(1)

# Close connection
device.disconnect()
adapter.stop()
