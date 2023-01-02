"""
Collect data from serial, get name and phases, start and end after a set time, find RMS and/or AM, 
export graph and values to a file
"""

import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import count
from math import sqrt

trial_duration = 45  # in seconds
serial_port = "COM3"


class Trial:
    arduino = serial.Serial(port=serial_port, baudrate=9600)

    def __init__(self, person, trial_number, action):
        self.person = person
        self.trail_number = trial_number
        self.action = action
        self.data_set = []
        self.graph = None
        self.rms = None
        self.am = None

    def serial_and_graph(self, i):
        """
        Reads from serial, records, and plots the data
        """

        try:
            count = next(self.index)
            self.xaxis.append(count)
            from_serial = Trial.arduino.readline().decode('utf-8').strip()
            temp = float(from_serial)
            self.data_set.append(temp)
        except:
            pass

        plt.cla()
        plt.ylabel("Voltage (V)")
        plt.xlabel("Time (1/10 seconds)")
        plt.plot(self.xaxis, self.data_set, linewidth=1)
        plt.tight_layout()

    def run_trial(self):
        """
        Runs the trial, animating graph and displaying it by running serial_and_graph, returns graph object
        """
        self.xaxis = []
        self.index = count()

        plt.style.use('fivethirtyeight')
        Trial.arduino.close()
        Trial.arduino.open()

        ani = FuncAnimation(plt.gcf(), self.serial_and_graph,
                            interval=10, frames=trial_duration*10, repeat=False, cache_frame_data=False)
        self.graph = plt.gcf()
        plt.show()
        plt.close()
        return self.graph

    def find_RMS(self):
        """
        Calculates RMS for trial given that the formula is sqrt((1/N) *  sum(N, n=1, Xn ^2)
        """
        sum_of_squares = sum([Xn ** 2 for Xn in self.data_set])
        rms = sqrt(((1/len(self.data_set)) * sum_of_squares))
        self.rms = rms
        return self.rms

    def find_AM(self):
        """
        Returns mean absolute value - basically averages data_set
        """
        self.am = sum(self.data_set)/len(self.data_set)
        return self.am

    def save_data(self):
        if self.rms and self.graph and self.data_set and self.am:  # makes sure there is data to save
            header = "{}-{}-{}".format(self.trail_number,
                                       self.person, self.action)
            self.graph.savefig("graphs/{}.png".format(header))

            with open("data.txt", "a") as f:
                f.write("\n\n" + header + "\n")
                f.write("Data: " + str(self.data_set) + "\n")
                f.write("RMS: " + str(self.rms) + "\n")
                f.write("AM: " + str(self.am) + "\n")

            print("saved")
        else:
            print("not saved")


def main():
    while True:
        name = input("\n\nPerson's name: ")
        activity = input("Activity: ")
        trial_number = input("Trial number: ")
        input("Press enter to begin")
        trial_ob = Trial(name, trial_number, activity)
        trial_ob.run_trial()
        print("\nRMS:" + str(trial_ob.find_RMS()))
        print("AM:" + str(trial_ob.find_AM()))
        save = input("Save data? (y/n) ")
        if save == "y":
            trial_ob.save_data()


main()
