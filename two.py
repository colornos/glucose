import logging
import pygatt
from pygatt.exceptions import NotConnectedError, BLEError
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

# Send RACP command to the device
def send_racp_command(device, command):
    try:
        racp_handle = device.get_handle("00002a52-0000-1000-8000-00805f9b34fb")
        device.char_write_handle(racp_handle, command)
    except pygatt.exceptions.NotConnectedError:
        log.error("Failed to send RACP command")

# Subscribe to the glucose measurement characteristic
def subscribe_to_glucose(device):
    try:
        glucose_handle = device.get_handle("00002a18-0000-1000-8000-00805f9b34fb")
        device.subscribe(glucose_handle, callback=process_glucose)
    except pygatt.exceptions.NotConnectedError:
        log.error("Failed to subscribe to glucose characteristic")

# Process the glucose measurement received
def process_glucose(handle, value):
    # Parse the glucose measurement value
    glucose = unpack("<h", value)[0] / 18.0
    log.debug("Received glucose measurement: {}".format(glucose))

# Main loop to read the latest glucose reading
while True:
    device = connect_device(ble_address)
    if device:
        # Send RACP command to read the latest glucose measurement
        send_racp_command(device, [1, 6])
        subscribe_to_glucose(device)
        log.debug("Waiting for glucose measurement...")

        try:
            # Wait for the measurement to arrive
            time.sleep(30)
        except (KeyboardInterrupt, SystemExit):
            log.debug("Exiting...")
            break
        except Exception as e:
            log.error("An error occurred: {}".format(e))

        try:
            # Disconnect from the device
            device.disconnect()
        except NotConnectedError:
            log.error("Failed to disconnect from device")
