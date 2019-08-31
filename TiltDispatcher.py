import threading
import time
import json
import requests
import TiltMonitor


class TiltDispatcher(threading.Thread):
    def __init__(self, beer_name):
        threading.Thread.__init__(self)
        self.transmitting = False
        self.beer_name = beer_name
        self.tilt_monitor = TiltMonitor.TiltMonitor()

    def run(self):
        self.transmitting = True
        while self.transmitting:
            val = self.tilt_monitor.get_tilt_data()
            time_point = time.time() / 86400 + 25569 + (2 / 24)
            converted_sg = val.gravity * 1000

            res = requests.post('http://monitor.beer/tilt/?Gjaerningsmenn', data={
                'Timepoint': time_point,
                'SG': converted_sg,
                'Temp': val.temperature,
                'Color': 'ORANGE',
                'Beer': self.beer_name,
                'Comment': '@',
            })
            json_response = res.json()
            time.sleep(5)

    def stop(self):
        self.transmitting = False
