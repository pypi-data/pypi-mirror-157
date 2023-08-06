import random
import os
import platform
import sys

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
def py2dmg(filename, iconFileName):
        setup = open("setup.py", "x")
        setup = open("setup.py", "w")
        setup.write("from setuptools import setup\n")
        setup.write(f"APP = ['{filename}']\n")
        setup.write("OPTIONS = {\n'iconfile':'{%s}',\n 'plist': {'CFBundleShortVersionString':'0.1.0'}\n}\n"%(iconFileName))
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
for arg in sys.argv:
    print(arg)