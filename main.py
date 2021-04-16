from cv2 import VideoCapture, CAP_PROP_FPS
from PIL import Image
from cuesdk import CueSdk
import time
import math
import numpy as np
import sys

# Hardcoded W:H values. Change as needed
WIDTH = 26
HEIGHT = 6

def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
    return leds

def scaleImage(img):
    return img.resize((WIDTH, HEIGHT), resample=Image.LANCZOS)

def getClosestPoint(c1, keyList):
    closest = 9999999
    targetKey = keyList[0]
    for key in keyList:
        c2 = key[1]
        # Just check distance between 2 xy coordinates
        dist = math.sqrt(abs(c1[0] - c2[0])**2 + abs(c1[1] - c2[1])**2)
        if dist < closest:
            closest = dist
            targetKey = key
    return targetKey

def main(color=True):
    global sdk

    sdk = CueSdk()
    connected = sdk.connect()
    
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    print("Running in color mode?", color)

    colors = get_available_leds()

    # I couldn't be bothered making this play on all devices because I only have 1 anyway, but it shouldn't be too hard to implement
    firstDevice = colors[0]
    
    keyList = []
    for c in firstDevice:
        keyList.append([c, firstDevice[c]])

    y = []
    x = []
    for c in keyList:
        x.append(c[1][0])
        y.append(c[1][1])
    
    # Normalize and get min/max
    # I had to add a bit to normalized X to make it cover the entire keyboard.
    normY = (np.max(y) - np.min(y))
    normX = (np.max(x) - np.min(x)) + 20
    yMin = np.min(y)
    xMin = np.min(x)

    for c in keyList:
        c[1] = ((c[1][0] - xMin)/normX * WIDTH, (c[1][1] - yMin)/normY * HEIGHT)

    video_path = "video.mp4"

    vcapture = VideoCapture(video_path)
    fps = vcapture.get(CAP_PROP_FPS)
    timeStep = 1/fps

    count = 0
    lastFrameCount = count
    success = True

    skipped = 0

    timeStepNano = timeStep * 1000000000

    timestamp = time.time_ns()
    startTime = time.time_ns()
    
    # Set every key to black, because we might not write to all keys, and it will throw an error if a key doesnt have rgb value
    for key in firstDevice:
        firstDevice[key] = (0, 0, 0)

    # Lets just map all the keys right now so we can skip checking the distance every frame
    keymap = []
    for y in range(HEIGHT):
        keymap.append([])
        for x in range(WIDTH):
            # We add 1 to y here, because apparently that makes the top row work properly.
            key = getClosestPoint((x, y+1), keyList)
            keymap[y].append(key)

    while success:
        if time.time_ns() - timestamp > 1000000000 - timeStepNano//2:
            print("FPS:", (count - lastFrameCount) - skipped, " | Skipped frames:", skipped)
            skipped = 0
            lastFrameCount = count
            timestamp = time.time_ns()

        targetTime = timeStepNano * count

        success, image = vcapture.read()
        while (time.time_ns() - startTime) > targetTime+timeStepNano*2:
            skipped += 1
            count += 1
            targetTime = timeStepNano * count
            success, image = vcapture.read()

        while (time.time_ns() - startTime) < targetTime:
            continue

        if success:
            image = Image.fromarray(image)
            if not color:
                image = image.convert('L')
                image = np.asarray(scaleImage(image).convert('RGB'))
            else:
                image = np.asarray(scaleImage(image))
                
            for y in range(len(image)):
                for x in range(len(image[y])):
                    key = keymap[y][x]
                    firstDevice[key[0]] = (int(image[y,x,2]), int(image[y,x,1]), int(image[y,x,0]))

            sdk.set_led_colors_buffer_by_device_index(0, firstDevice)
            sdk.set_led_colors_flush_buffer()

        count += 1

#
# Run "python main.py bw" if you wanna run in black&white mode
#
if __name__ == "__main__":
    args = sys.argv
    
    bW = len(args) > 1 and args[1] == "bw"

    main(color=(not bW))