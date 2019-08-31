import TiltHydrometer
import time


class TiltMonitor:
    def __init__(self):
        self.tilt_hydrometer = TiltHydrometer.TiltHydrometerManager(False, 60, 40)
        self.tilt_hydrometer.loadSettings()
        self.isListening = False
        self.transmitting = False
        self.beer_name = ''

    def start_listening(self):
        self.tilt_hydrometer.start()
        self.isListening = True

    def stop_listening(self):
        self.tilt_hydrometer.stop()
        self.isListening = False

    def get_tilt_data(self):
        if not self.isListening:
            self.start_listening()

        val = None
        while val is None:
            val = self.tilt_hydrometer.getValue('Orange')
            time.sleep(0.1)
        # Got a value
        self.stop_listening()
        return val
