
## Linux/MacOS build light script for USB Led devices (eg. Delcom USB Visual Signal Indicator)

This script polls a hudson instance and drives an USB led device to act as a "build light".

It works out of the box for Linux. For MacOS libusb 1.x must be installed:

    sudo brew install libusb

To configure the script for your hudson instance, change the following line by the end of run.py:

    build_light = HudsonBuildLight(host='127.0.0.1', port=8080, job='your-job-here')
