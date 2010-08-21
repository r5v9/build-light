
# for mac os install libusb using: brew install libusb
# bundled pyusb is 1.0.0-a0

import httplib
import time
import os
import sys
import re

try:
	import usb.core
	import usb.util
except Exception:
	pass # only required for mac os

class UsbLedLinux:    
    
    def __init__(self):
        usbled_devices_folder = '/sys/bus/usb/drivers/usbled/'
        devices = filter(lambda f: re.match('[0-9]', f), os.listdir(usbled_devices_folder))
        if len(devices)==0:
            print 'No device found'
            sys.exit(1)
        self.device_folder = usbled_devices_folder + devices[0] + '/'
    
    def set_light(self, color, status):
        f = open(self.device_folder + color, "w")
        f.write(str(status))
        f.close()

    def red(self):
        self.off()
        self.set_light('red', 1)

    def green(self):
        self.off()
        self.set_light('green', 1)

    def blue(self):
        self.off()
        self.set_light('blue', 1)

    def off(self):
        self.set_light("blue", 0)
        self.set_light("green", 0)
        self.set_light("red", 0)

class UsbLedMac:
    
    def __init__(self):
        self.dev = usb.core.find(idVendor=0x0fc5, idProduct=0x1223)
        if self.dev is None:
            raise ValueError('Device not found')
        self.dev.set_configuration()

    def send(self, color):
        try:
            self.dev.ctrl_transfer(bmRequestType=0x000000c8,
                                   bRequest= 0x00000012,
                                   wValue=(0x02 * 0x100) + 0x0a,
                                   wIndex=0xff & (~color),
                                   data_or_wLength=0x00000008)

        # a pipe error is thrown even if the operation is successful
        except usb.core.USBError: 
            pass
    
    def red(self):
        self.send(0x02)
    
    def green(self):
        self.send(0x01)

    def blue(self):
        self.send(0x04)

    def off(self):
        self.send(0x00)

class HudsonBuildLight:
        
    def __init__(self, host, port, job):
        self.host = host
        self.port = port
        self.job = job
        self.usbled = self.get_usbled()
        
        # not mapped colors will default to blue
        # other colors returned by hudson: blue_anime red_anime grey grey_anime aborted
        self.color_map = { 'blue':'green', 'red':'red' }
        self.default_color = 'blue'

    def get_usbled(self):
        platform = os.uname()[0].lower()
        usbled_platform_map = { 'darwin':UsbLedMac, 'linux':UsbLedLinux }
        if platform not in usbled_platform_map.keys():
            print 'this platform (%s) is not supported' % platform
            sys.exit(1)
        return usbled_platform_map[platform]()

    def get_job_color(self):
        try:
            conn = httplib.HTTPConnection(self.host, self.port)
            conn.request('GET','/job/%s/api/python' % self.job)
            job = eval(conn.getresponse().read())
        except Exception:
            return self.default_color

        job_color = job['color']
        if self.color_map.has_key(job_color):
            return self.color_map[job_color]
        else:
            return self.default_color
        
    def set_usbled_color(self, color):
        methods_map = { 'red':self.usbled.red, 'green':self.usbled.green, 'blue':self.usbled.blue, 'off':self.usbled.off }
        method = methods_map[color]
        method()

    def loop(self):
        self.set_usbled_color(self.default_color)
        last_color = self.get_job_color()
        self.set_usbled_color(last_color)
        while True:
            color = self.get_job_color()
            if color != last_color:
                self.set_usbled_color(color)
                last_color = color
            time.sleep(1)
