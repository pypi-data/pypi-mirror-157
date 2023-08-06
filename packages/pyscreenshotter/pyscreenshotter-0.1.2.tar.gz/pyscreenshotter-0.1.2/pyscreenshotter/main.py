#!/usr/bin/env python3
import numpy as np
import cv2
import pyautogui
import keyboard
import os
import re
import sys

# How many zeros to add
PADBY: int = 4

# Returns the last screenshot in current dirs number.
def getLastScreenshotNumber()->int:
    dir = os.listdir("./") #['file1', 'file2']
    pattern: str = ".png"
    for i in range(PADBY):
        pattern = "\d"+pattern

    number: int = 0

    for i in dir:
        if(re.match(pattern, i)):
            if(int(i[:-4]) > number):
                number = int(i[:-4])

    return number

# Pad a given int by given amount of zeros
def padInt(n: int)->str:
    global PADBY
    paddedNum: str = str(n)

    for i in range(PADBY):
        if(len(paddedNum) < PADBY):
            paddedNum = "0"+paddedNum

    return paddedNum

def take_screenshot(screenshot_name: str):
    # take screenshot using pyautogui
    image = pyautogui.screenshot()

    # since the pyautogui takes as a
    # PIL(pillow) and in RGB we need to
    # convert it to numpy array and BGR
    # so we can write it to the disk
    image = cv2.cvtColor(np.array(image),
                        cv2.COLOR_RGB2BGR)

    # writing it to the disk using opencv

    cv2.imwrite(f"{screenshot_name}.png" , image)


def main():
    print(sys.argv) # cmdlin args
    cmdline_args: list = sys.argv

    # Define keybinds
    if(len(cmdline_args) > 1):
        capture_key = cmdline_args[1]
        quit_key = cmdline_args[2]
    else:
        capture_key = "s"
        quit_key = "q"

    while True:
        if(keyboard.is_pressed(capture_key)):
            lastScreenshotNumber: int = getLastScreenshotNumber()
            lastScreenshotNumber+=1
            paddedNum: str = padInt(lastScreenshotNumber)
            take_screenshot(paddedNum)
            print(f"SNAP! {paddedNum}.png")
        elif(keyboard.is_pressed(quit_key)):
            exit()

if __name__ == '__main__':
    main()
