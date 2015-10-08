#!/usr/bin/python

import os
import sys
import time
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
        
        self.dev = usb.core.find(idVendor=0x2123, idProduct=0x1010)

        if self.dev is None:
            print("Error!")
            exit(1)
        
        try:
                self.dev.detach_kernel_driver(0)
        except Exception, c:
            pass

        self.dev.set_configuration()

    def cmd(self, cmd):
        self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,cmd,0x00,0x00,0x00,0x00,0x00,0x00]) 

    def command(self, cmd, duration):
        self.cmd(cmd)
        time.sleep(duration)
        self.cmd(self.STOP)

    def left(self, duration):
        self.command(self.commands['LEFT'], duration)

    def right(self, duration):
        self.command(self.commands['RIGHT'], duration)

    def up(self, duration):
        self.command(self.commands['UP'], duration)

    def down(self, duration):
        self.command(self.commands['DOWN'], duration)

    def fire(self):
        self.cmd(self.commands['FIRE'])

if __name__ == '__main__':
    
    l = controller()
    print l.dev
    l.up(2)
    l.left(8)
    l.right(8)
    l.down(2)
    l.left(4)
    l.up(1)
    #l.fire()

