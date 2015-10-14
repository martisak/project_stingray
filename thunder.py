#!/usr/bin/python

import os
import sys
import threading
import time
import logging
import usb.core

class controller():

    commands = {
        "DOWN": 0x01,
        "UP":  0x02,
        "LEFT": 0x04,
        "RIGHT": 0x08,
        "FIRE": 0x10,
        "STOP": 0x20
    }

    def __init__(self):

        logging.info("Created launcher.")
        self.dev = usb.core.find(idVendor=0x2123, idProduct=0x1010)
        self.t = None

        if self.dev is None:
            print("Error!")
            exit(1)

        try:

            logging.info("Reset device.")
            self.dev.reset()
            logging.info("Detaching kernel driver")
            self.dev.detach_kernel_driver(0)

        except Exception, c:
            logging.warning("Exception in creating launcher.")
            pass

        logging.info("Setting configuration.")
        self.dev.set_configuration()

    def cmd(self, cmd):
        self.dev.ctrl_transfer(
            0x21, 0x09, 0, 0, [0x02, cmd, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def runcommand(self, cmd, duration):
            logging.info("Running command." + str(cmd), extra={"command": cmd})
            self.cmd(cmd)
            time.sleep(duration)
            self.cmd(self.commands['STOP'])
            logging.info("Finished running command." + str(cmd), extra={"command": cmd})

    def command(self, cmd, duration):
        logging.info("Command", extra={"command": cmd, "duration": duration})

        logging.debug("Number of active threads: " +
                      str(threading.active_count()))

        if threading.active_count() <= 1:
            self.t = threading.Thread(
                target=self.runcommand,
                args=(cmd, duration)
            )

            self.t.start()

        else:
            logging.debug("Can't slew. Thread already active")

    def left(self, duration):
        self.command(self.commands['LEFT'], duration)

    def right(self, duration):
        self.command(self.commands['RIGHT'], duration)

    def up(self, duration):
        self.command(self.commands['UP'], duration)

    def down(self, duration):
        self.command(self.commands['DOWN'], duration)

    """
    Returns true if there is a thread active (indicating that the turret is slewing)
    """ 
    def isSlewing(self):
        if threading.active_count() > 1:
            return True
        return False

    def fire(self):
        if threading.active_count() <= 1:
            logging.debug("Firing")
            self.cmd(self.commands['FIRE'])
        else:
            logging.debug("Can't fire. Thread already active")

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                    format='(%(asctime)s %(name)-12s %(levelname)-8s %(threadName)-10s) %(message)s',
                    )

    l = controller()
    
    print l.dev 
    #l.right(5)
    l.fire()
    #time.sleep(6)
    #l.left(5)
    #time.sleep(5.1)

    #l.up(2)
    #time.sleep(0.1)
    #l.down(2)
    #time.sleep(3)

    l.fire()
    time.sleep(2)