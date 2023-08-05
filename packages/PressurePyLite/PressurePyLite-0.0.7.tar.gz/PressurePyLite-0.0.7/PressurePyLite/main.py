from PressurePyLite.ardu import Arduino

import argparse
import time
from datetime import datetime
import csv


def save(filename, time_, pressure):
    """save time and pressure to a csv - this function adds a row into an existing csv file"""
    fields = [time_, pressure]
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(fields)


def main():
    """
    main function
    is defined as entrypoint if PressurePyLite is installed via pip
    """


    ####
    # parse arguments when program starts
    ####
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--sensor", required=False,
                    help="change the port of the sensor arduino")
    ap.add_argument("-p", "--pump", required=False,
                    help="change the port of the pump arduino")
    ap.add_argument("-t", "--target_pressure", required=False,
                    help="change the pressure")
    args = vars(ap.parse_args())


    ####
    # set defaults if no argument was given
    ####
    if args["sensor"] is None:
        # sensor = "/dev/cu.usbserial-2320"
        sensor = "/dev/ttyUSB0"
    else:
        sensor = args["sensor"]
    if args["pump"] is None:
        # pump = "/dev/cu.usbmodem23301"
        pump = "/dev/ttyACM0"
    else:
        pump = args["pump"]
    if args["target_pressure"] is None:
        target_pressure = 120
    else:
        target_pressure = args["target_pressure"]


    # instantiate class / connection to arduino
    ardu = Arduino(sensor, pump, target_pressure)

    # create the save file
    filename = datetime.now().strftime("%d_%m_%Y")+"_pressure.csv"  # create filename "[TIMESTAMP]_pressure.csv"
    with open(filename, "w") as my_empty_csv:                       # open file once to create it
        pass

    while True:
        p, t = ardu.read_port()                                     # read data from the sensor
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")          # current timestamp
        # save to file
        save(filename, now, p)                                      # save to csv
        print("Druck: "+str(p))                                     # print to terminal
        print("Time: "+now)
        print(" ")
        # send to pump
        ardu.pump_connect(p, "go")                                  # tells the pump ardu the target pressure and let's him start
        time.sleep(2)                                               # waiting 2 seconds


if __name__ == "__main__":
    main()
