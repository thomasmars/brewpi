import json
import bluetooth
from TiltMonitor import TiltMonitor
from WifiMonitor import WifiMonitor
import subprocess
import os
import WPASupplicantController
from TiltDispatcher import TiltDispatcher

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = bluetooth.PORT_ANY
uuid = "00001101-0000-1000-8000-00805f9b34fb"
server_sock.bind(("", port))
server_sock.listen(5)

bluetooth.advertise_service(
    server_sock,
    "Test server",
    service_id=uuid,
    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE]
)

port = server_sock.getsockname()[1]
tilt_monitor = TiltMonitor()
wifi_monitor = WifiMonitor()
tilt_dispatcher = None
beer_name = ''

idx = 0
tilt_data_count = 0
while True:

    print("WAITING for connection on RFCOMM channel %d" % port)
    # accept connections and create the client socket
    client_sock, address = server_sock.accept()
    print("Accepted connection from ", address)
    # now everything is set-up we're ready to receive data
    tilt_data_count = 0

    while True:
        try:
            print "Waiting for command..."
            data = client_sock.recv(1024)
            if len(data) == 0:
                break
            data = json.loads(data)
            event = data['message']

            if event == 'reboot':
                os.system('/sbin/reboot')

            if event == 'tilt':
                val = tilt_monitor.get_tilt_data()
                message = {
                    'sg': val.gravity,
                    'temp': val.temperature,
                    'message': 'tilt',
                    'count': tilt_data_count
                }
                client_sock.send(json.dumps(message))
                tilt_data_count += 1

            if event == 'get-networks':
                networks = wifi_monitor.get_networks()
                formatted_network = list(
                    map(
                        lambda x: {
                            'address': x.address,
                            'ssid': x.ssid,
                            'signal': x.signal,
                        },
                        networks
                    )
                )
                message = {
                    'networks': formatted_network,
                    'message': 'networks',
                }

                client_sock.send(json.dumps(message))

            if event == 'get-saved-networks':
                networks = WPASupplicantController.get_saved_networks()
                formatted_network = list(map(
                    lambda x: {
                        'ssid': x['ssid'],
                    },
                    networks
                ))
                message = {
                    'networks': formatted_network,
                    'message': 'saved-networks',
                }
                client_sock.send(json.dumps(message))

            if event == 'connect':
                password = data['password']
                ssid = data['ssid']
                WPASupplicantController.store_network(ssid, password)
                message = {
                    'message': 'connected',
                    'success': True,
                }
                client_sock.send(json.dumps(message))

            if event == 'get-connected-network':
                network = subprocess.check_output(
                    '/sbin/iwgetid | awk \'{split($0, a, ":"); print a[2]}\'',
                    shell=True
                )
                network = network.replace('"', '')
                message = {
                    'message': 'connected-network',
                    'network': network,
                }
                client_sock.send(json.dumps(message))

            if event == 'delete-network':
                ssid = data['ssid']
                WPASupplicantController.remove_network(ssid)
                message = {
                    'message': 'deleted',
                    'success': True,
                }
                client_sock.send(json.dumps(message))

            if event == 'activate-network':
                ssid = data['ssid']
                message = {
                    'message': 'connected',
                    'success': True,
                }
                client_sock.send(json.dumps(message))

            if event == "ping":
                IP = '8.8.8.8'
                ping_command = "ping -c 5 -n -W 4 " + IP
                (output, error) = subprocess.Popen(
                    ping_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                ).communicate()
                averagePing = False
                if not error:
                    lines = output.split('\n')
                    rttLine = lines[-2]
                    numbers = rttLine[23:]
                    values = numbers.split('/')
                    averagePing = values[1]

                message = {
                    'message': 'ping',
                    'ping': averagePing,
                    'success': averagePing is not False,
                }
                client_sock.send(json.dumps(message))

            if event == 'set_name':
                name = data['name']
                beer_name = name

            if event == 'start_dispatching':
                if beer_name is not None:
                    tilt_dispatcher = TiltDispatcher(beer_name)
                    tilt_dispatcher.start()

            if event == 'stop_dispatching':
                if tilt_dispatcher is not None:
                    tilt_dispatcher.stop()

        except IOError:
            print("invalid socket!, Break to accept connection!")
            # Break out of socket connection
            break

# when finished be sure to close your sockets
# client_sock.close()
# server_sock.close()
