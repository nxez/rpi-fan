#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 NXEZ.COM.
# http://www.nxez.com
#
# Licensed under the GNU General Public License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.gnu.org/licenses/gpl-2.0.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# tutorials url: http://shumeipai.nxez.com/

__author__ = 'Spoony'
__license__  = 'Copyright (c) 2020 NXEZ.COM'

import time
import RPi.GPIO as GPIO

PIN_FAN = 18
speed_base = 70
speed_step = 1.5
threshold_temp = 40

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_FAN, GPIO.OUT)

def get_cpu_temp():
    temp_file = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = temp_file.read()
    temp_file.close()
    return float(cpu_temp) / 1000

def get_scaling_cur_freq():
    temp_file = open( "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq" )
    scaling_cur_freq = temp_file.read()
    temp_file.close()
    return float(scaling_cur_freq) / 1000

def get_scaling_max_freq():
    temp_file = open( "/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq" )
    scaling_max_freq = temp_file.read()
    temp_file.close()
    return float(scaling_max_freq) / 1000

if __name__ == "__main__":
    p = GPIO.PWM(PIN_FAN, 10)
    p.start(100)
    time.sleep(0.05)
    scaling_max_freq = get_scaling_max_freq()
    speed = 0
    try:
        while True:
            current_temp = get_cpu_temp()
            scaling_cur_freq = get_scaling_cur_freq()

            if (current_temp < threshold_temp):
                speed = 0
            else:
                speed = speed_base + (current_temp - threshold_temp) * speed_step

            if (scaling_cur_freq == scaling_max_freq):
                pass
                speed = 100

            if speed > 100:
                speed = 100

            if (speed > 0):
                p.ChangeDutyCycle(100)
                time.sleep(0.05)
                p.ChangeDutyCycle(speed)
            else:
                p.ChangeDutyCycle(speed)

            print("TEMP: %.2f, FREQ: %d/%d MHz, FAN SPEED: %d%%" % (current_temp, scaling_cur_freq, scaling_max_freq, speed))
            time.sleep(3)

    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()
