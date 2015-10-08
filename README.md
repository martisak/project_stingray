# Project Stingray

This is a face-tracking autonomous foam-missile launcher. It aims for your eyes - you have been warned! 

## Acknowledgements

There are many similar projects out there - here are a few that I found interesting. This project has been heavily influenced by these.

* [Basic motion detection and tracking with Python and OpenCV](http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/)

## Parts

* [Raspberry Pi 2](https://www.raspberrypi.org/products/raspberry-pi-2-model-b/)
* A camera. I used the [Raspberry Pi Camera Module](https://www.raspberrypi.org/products/camera-module/)
* [Thunder USB Missile Launcher](http://dreamcheeky.com/thunder-missile-launcher)
* USB Hub (since the missile launcher draws more current than the Raspberry USB ports can supply.)


## Step by step instructions

* Make sure the pi user has access to the USB port. You could also run with sudo. 

```bash
pi@node3 ~ $ lsusb
Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. 
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. 
Bus 001 Device 008: ID 04d9:0022 Holtek Semiconductor, Inc. Portable Keyboard
Bus 001 Device 004: ID 2101:8500 ActionStar 
Bus 001 Device 005: ID 0bda:8176 Realtek Semiconductor Corp. RTL8188CUS 802.11n WLAN Adapter
Bus 001 Device 006: ID 2101:8501 ActionStar 
Bus 001 Device 007: ID 2123:1010  

pi@node3 ~ $ sudo chmod a+rw /dev/bus/usb/001/007
```
