import subprocess
import uuid
wpa_path = '/etc/wpa_supplicant/wpa_supplicant.conf'


def get_saved_networks():
    try:
        wpa_networks = subprocess.check_output(
            'cat /etc/wpa_supplicant/wpa_supplicant.conf | grep network -nA 4',
            shell=True
        )
    except subprocess.CalledProcessError:
        return []

    networks = wpa_networks.replace('\t', '').split('--\n')
    formatted_networks = []
    for single_network in networks:
        lines = single_network.split('\n')
        network_start_line = lines[0].split(':')[0]
        no_breaks = lines[1:-2]

        network = {
            'start_line': network_start_line,
        }
        for line in no_breaks:
            [key, value] = line.split('-')[1].split('=')
            network[key] = value
        formatted_networks.append(network)
    return formatted_networks


def store_network(ssid, password):
    unique_name = uuid.uuid1()
    network = {
        'ssid': '"' + ssid + '"',
        'psk': '"' + password + '"',
        'key_mgmt': 'WPA-PSK',
        'id_str': '"' + str(unique_name) + '"',
    }
    formatted_network = 'network={'
    for key in network:
        formatted_network += '\n\t' + key + '=' + network[key]
    formatted_network += '\n}\n'
    f = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a+')
    f.write(formatted_network)
    f.close()


def remove_network(ssid):
    saved_networks = get_saved_networks()
    network = list(filter(lambda x: x['ssid'] == ssid, saved_networks))
    if len(network) == 0:
        return
    network = network[0]
    start_line = network['start_line']
    end_line = str(int(start_line) + 5)
    command = 'sed -i \'' + start_line + ',' + end_line + 'd\' ' + wpa_path
    subprocess.check_output(command, shell=True)
