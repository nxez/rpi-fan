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
from apa102_pi.driver import apa102

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

def led_show(temp):
    strip = apa102.APA102(num_led=4, global_brightness=20, mosi=17, sclk=4, order='rgb')
    c_temp = [0x000008, 0x000800, 0x080800, 0x080008, 0x080000]

    c_temp_i = 4
    if temp < 60:
        c_temp_i = 3
    if temp < 55:
        c_temp_i = 2
    if temp < 50:
        c_temp_i = 1
    if temp < 40:
        c_temp_i = 0

    strip.set_pixel_rgb(0, c_temp[c_temp_i])

    for j in range(3, 0, -1):
         strip.set_pixel_rgb(j, 0x000000)

    if c_temp_i > 0:
        strip.set_pixel_rgb(1, c_temp[c_temp_i - 1])
        strip.show()
        time.sleep(0.2)
        strip.set_pixel_rgb(1, 0x000000)
        strip.set_pixel_rgb(2, c_temp[c_temp_i - 1])
        strip.show()
        time.sleep(0.2)
        strip.set_pixel_rgb(2, 0x000000)
        strip.set_pixel_rgb(3, c_temp[c_temp_i - 1])
        strip.show()
        time.sleep(0.2)
        strip.set_pixel_rgb(3, 0x000000)
        strip.set_pixel_rgb(2, c_temp[c_temp_i - 1])
        strip.show()
        time.sleep(0.2)
        strip.set_pixel_rgb(2, 0x000000)
        strip.set_pixel_rgb(1, c_temp[c_temp_i - 1])
        strip.show()
        time.sleep(0.2)
    else:
        strip.show()
        time.sleep(1)

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
            led_show(current_temp)
            #time.sleep(3)

    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()
