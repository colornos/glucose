import logging
import pygatt
from pygatt.exceptions import NotConnectedError, BLEError
import time
from struct import unpack

# Create a logger for logging debugging information
logging.basicConfig(level=logging.DEBUG)
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
    except (BLEError, NotConnectedError) as e:
        log.error("Failed to connect to device: {}".format(e))
        return None

# Subscribe to the glucose measurement characteristic
def subscribe_to_glucose(device):
    try:
        glucose_handle = device.get_handle("00002a18-0000-1000-8000-00805f9b34fb")
        device.subscribe(glucose_handle, callback=process_glucose)
    except NotConnectedError as e:
        log.error("Failed to subscribe to glucose characteristic: {}".format(e))

# Process the glucose measurement received
def process_glucose(handle, value):
    # Parse the glucose measurement value
    glucose = unpack("<h", value)[0] / 18.0
    log.debug("Received glucose measurement: {}".format(glucose))
    return glucose

# Main loop to read the latest glucose reading
glucose_measurement = None
while True:
    device = connect_device(ble_address)
    if device:
        subscribe_to_glucose(device)
        log.debug("Waiting for glucose measurement...")
        time.sleep(30)
        try:
            device.disconnect()
            glucose_measurement = process_glucose(handle, value)
        except NotConnectedError as e:
            log.error("Failed to disconnect from device: {}".format(e))
            break
    else:
        log.debug("Failed to connect to the device, trying again in 30 seconds")
        time.sleep(30)

log.debug("Latest glucose measurement: {}".format(glucose_measurement))
