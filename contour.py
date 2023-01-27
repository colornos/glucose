import logging
import pygatt
from pygatt.exceptions import NotConnectedError

# Create a logger for logging debugging information
log = logging.getLogger(__name__)

# Get the BLE address and device name from the configuration file
ble_address = "00:0a:e2:64:25:86"
device_name = "CONTOURONE-586"

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
        subscribe_to_glucose(device)
        log.debug("Waiting for glucose measurement...")
        time.sleep(30)
        try:
            device.disconnect()
        except NotConnectedError:
            log.error("Failed to disconnect from device")
            break
