import logging
import pygatt
from pygatt.exceptions import NotConnectedError, NotificationTimeout
import time
from struct import unpack

# Create a logger for logging debugging information
log = logging.getLogger(__name__)

# Get the BLE address and device name from the configuration file
ble_address = "00:81:F9:B2:24:74"
device_name = "Contour7830H7002817"

# Connect to the glucose meter device
def connect_device(ble_address):
    try:
        adapter = pygatt.GATTToolBackend()
        adapter.start()
        device = adapter.connect(ble_address)
        return device
    except pygatt.exceptions.NotConnectedError:
        log.error("Failed to connect to device")
        return None

# Send RACP command to read all records
def read_all_records(device):
    try:
        racp_handle = device.get_handle("00002a52-0000-1000-8000-00805f9b34fb")
        device.char_write_handle(racp_handle, [1,1])
    except pygatt.exceptions.NotConnectedError:
        log.error("Failed to send RACP command to read all records")

# Send RACP command to read last record received
def read_last_record(device):
    try:
        racp_handle = device.get_handle("00002a52-0000-1000-8000-00805f9b34fb")
        device.char_write_handle(racp_handle, [1,6])
    except pygatt.exceptions.NotConnectedError:
        log.error("Failed to send RACP command to read last record")

# Send RACP command to read number of records
def read_number_of_records(device):
    try:
        racp_handle = device.get_handle("00002a52-0000-1000-8000-00805f9b34fb")
        device.char_write_handle(racp_handle, [4,1])
    except pygatt.exceptions.NotConnectedError:
        log.error("Failed to send RACP command to read number of records")

# Send RACP command to read extract from record 45 onwards
def read_extract_from_record(device):
    try:
        racp_handle = device.get_handle("00002a52-0000-1000-8000-00805f9b34fb")
        device.char_write_handle(racp_handle, [1,3,1,45,0])
    except pygatt.exceptions.NotConnectedError:
        log.error("Failed to send RACP command to read extract from record 45")

# Subscribe to the glucose measurement characteristic
def subscribe_to_glucose(device):
    try:
        glucose_handle = device.get_handle("00002a18-0000-1000-8000-00805f9b34fb")
        device.subscribe(glucose_handle
