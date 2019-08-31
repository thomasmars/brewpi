from wifi import Cell, Scheme


class WifiMonitor:
    def __init__(self):
        self.interface = 'wlan0'

    def get_networks(self):
        return Cell.all(self.interface)

    def get_network(self, network_ssid):
        networks = self.get_networks()
        network = list(filter(lambda x: x.ssid == network_ssid, networks))[0]
        return network

    @staticmethod
    def get_saved_networks():
        saved_networks = []
        for scheme in Scheme.all():
            saved_networks.append(scheme)
        return saved_networks

    def get_saved_network(self, network_ssid):
        networks = self.get_saved_networks()
        network = list(
            filter(
                lambda x: x.options['wpa-ssid'] == network_ssid,
                networks
            )
        )[0]
        return network

    def save_network(self, network_ssid, password):
        network = self.get_network(network_ssid)
        saved_networks = self.get_saved_networks()
        saved_networks_count = len(saved_networks)
        new_network = Scheme.for_cell(
            self.interface,
            'network_' + str(saved_networks_count),
            network,
            password
        )
        new_network.save()

    def remove_network(self, network_ssid):
        network = self.get_saved_network(network_ssid)
        network.delete()

    def connect_network(self, network_ssid):
        network = self.get_saved_network(network_ssid)
        try:
            network.activate()
        except Exception, e:
            return False
        return True
