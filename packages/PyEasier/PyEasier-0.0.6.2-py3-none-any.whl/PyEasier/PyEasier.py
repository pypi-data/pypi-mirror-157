import math
import random
import os
import platform
import psutil

PI = 3.141592
PHI = 1.618033

def ranNum(low, high):
    return random.randint(low, high)
def ranFloat(low, high):
    return random.uniform(low, high)
def cap(num, decimalPlaces):
    return format(num, f".{decimalPlaces}f")
def package(module):
    os.system(f"pip install {module}")
def runCmd(cmd):
    os.system(cmd)
def osName():
    return platform.system()
def py2dmg(filename):
        setup = open("setup.py", "x")
        setup = open("setup.py", "w")
        setup.write("from setuptools import setup\n")
        setup.write(f"APP = ['{filename}']\n")
        setup.write("OPTIONS = {\n'argv_emulation':True\n}\n")
        setup.write("setup(\napp = APP, \noptions = {\n'py2app': OPTIONS\n}, \nsetup_requires = ['py2app'])\n")
        setup.close()
        os.system("python setup.py py2app")

def py2exe(filename, console=False, iconFileName = ''):
    if console == False:
        os.system(f'pyinstaller --onefile --noconsole "{filename}"')
    elif console == False and iconFileName != '':
        os.system(f'pyinstaller --onefile --noconsole --icon = "{iconFileName}" "{filename}"')
    elif console == True:
        os.system(f'pyinstaller --onefile "{filename}"')
    elif console == True and iconFileName != '':
        os.system(f'pyinstaller --onefile --icon = "{iconFileName}" "{filename}"')

def write(filename, text):
    file = open(filename, "w")
    file.write(text)
    file.close()


def read(filename, mode = 't'):
    if mode == 't':
        with open(filename, "r") as file:
            return file.readlines()
        file.close()
    else:
        with open(filename, "rb") as file:
            return file.readlines()
        file.close()

def append(filename, text):
    with open(filename, "a+") as f:
        f.write(text)
def create(filename):
    open(filename, "x")
def technoblade():
    print("🐷😞Rip Techno you will be missed 😞🐷")
def cos(num):
    return math.cos(num)
def sin(num):
    return math.sin(num)
def acos(num):
    return math.acos(num)
def asin(num):
    return math.asin(num)
def tan(num):
    return math.tan(num)
def log(num, base):
    return math.log(num, base)
def delete(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print(f'✨ Deleted {filename} ✨')
    else:
        print(f'Hey! What are you trying to do here? There is no file named {filename} ya doof 😡')

def getBatteryLevel():
    battery = psutil.sensors_battery()
    percent = battery.percent
    return percent
def isPluggedIn():
    battery = psutil.sensors_battery()
    plugged = battery.power_plugged
    return plugged
def findCircumference(radius):
    return radius*PI*2
def findRadius(circumference):
    return round(circumference/6.283184, 2)
def findDiameter(radius):
    return 2*radius
