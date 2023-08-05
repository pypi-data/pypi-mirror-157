import serial
import time


class Arduino:
    """
    class with connection to two arduinos - one connected to a sensor and the other one connected to a pump
    default ports for raspberry pi: ardu = Arduino("/dev/cu.usbserial-2320", "/dev/cu.usbmodem23301")
    """

    sensor: serial
    pump: serial
    target_pressure: float
    experiment_started: bool
    counter: int

    def __init__(self, sensor_port, pump_port, target_pressure):
        """ Set the Ports and logs the files """

        self.sensor = serial.Serial(sensor_port, '9600')        # connect to the sensor arduino
        self.pump = serial.Serial(pump_port, '9600')            # connect to the pump arduino
        self.target_pressure = target_pressure                  # set the target pressure
        self.experiment_started = False                         # not needed atm
        self.counter = 0                                        # not needed atm

    def read_port(self):
        """reads a bytecode from the sensor arduino and converts it to 2 integers (pressure/temperature)"""
        # make sure to read the last line sent
        bytes_ = self.sensor.readlines(1)[-1]
        while self.sensor.inWaiting() > 0:
            time.sleep(0.05)
            bytes_ = self.sensor.readlines(1)[-1]
            time.sleep(0.05)

        # convert bytes to string
        str_rn = bytes_.decode()
        str_ = str_rn.rstrip()
        split = str_.split('/')

        # the format is: "pressure/temperature"
        return float(split[0]), float(split[1])


    def pump_connect(self, pressure, status):
        """sends current pressure and target pressure to the pump arduino as bytes - arduino will then pump or not pump"""
        self.pump.write(bytes(str(pressure) + '/' + str(self.target_pressure) + '/' + str(status) + '/\n', 'utf-8'))    # \n is important because arduino is reading the serial input line by line
