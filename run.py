#!/usr/bin/env python

from buildlight import HudsonBuildLight

if __name__ == '__main__':
    build_light = HudsonBuildLight(host='127.0.0.1', port=8080, job='your-job-here')
    build_light.loop()