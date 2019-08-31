# How to use
bluetoothServer.py is the main executable that the pi should run on startup, which starts the bluetooth server.
It allows you to connect a bluetooth device that can send messages to the server.

The server will handle:
- Setting up wifi for the pi
- Reading from a tilt hydrometer
- Sending tilt hydrometer data to a monitor.beer account, or an alternative cloud beer visualization system

## Components
blescan is an iBeacon scanner, which allows us to capture data from the tilt.

TiltHydrometer is a library for getting the data from the Tilt Hydrometer

###TiltDispatcher
Sends Tilt data to a cloud endpoint

### TiltMonitor
Handles starting listening for temperature and gravity from the tilt

### WifiMonitor/WPASupplicantController
Handles finding, connecting to and removing wifi networks for the pi, which are needed in order to send the tilt data to a cloud solution
 