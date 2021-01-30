from cv2 import VideoCapture, CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH, CAP_PROP_FPS, VideoWriter, VideoWriter_fourcc
from PIL import Image
from cuesdk import CueSdk
import time
import math
import numpy as np

def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
    return leds

# Hardcoded W:H values for keyboard because I'm lazy
def scaleImage(img):
    return img.resize((24, 6), resample=Image.ANTIALIAS)
    # return img.resize((24, 6), resample=Image.LANCZOS)

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

def main():
    global sdk

    sdk = CueSdk()
    connected = sdk.connect()
    
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

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
    normY = (np.max(y) - np.min(y))
    normX = (np.max(x) - np.min(x))
    yMin = np.min(y)
    xMin = np.min(x)

    # Make sure the keyvals X:Y are set to 24:6 (just because the keyboard has basically 6 rows and 24 keys as width)
    for c in keyList:
        c[1] = ((c[1][0] - xMin)/normX * 24, (c[1][1] - yMin)/normY * 6)

    video_path = "video.mp4"

    vcapture = VideoCapture(video_path)
    fps = vcapture.get(CAP_PROP_FPS)
    timeStep = 1/fps

    count = 0
    success = True

    accTDiff = 0
    
    # Reset every key to black, because we might not write to all keys, and it will throw an error if a key doesnt have rgb value
    for key in firstDevice:
        firstDevice[key] = (0, 0, 0)

    while success:
        print("frame: ", count)
        # Read next image
        success, image = vcapture.read()
        if accTDiff >= timeStep:
            print("Frameskip, accTDiff was", accTDiff)
            accTDiff -= timeStep
        elif success:
            t = time.time_ns()

            # OpenCV returns images as BGR, remember to convert to RGB (either here or when setting LED)
            # image = Image.fromarray(image[..., ::-1])
            image = Image.fromarray(image)
            image = np.asarray(scaleImage(image))

            for y in range(len(image)):
                for x in range(len(image[y])):
                    key = getClosestPoint((x, y), keyList)
                    firstDevice[key[0]] = (int(image[y,x,2]), int(image[y,x,1]), int(image[y,x,0]))

            sdk.set_led_colors_buffer_by_device_index(0, firstDevice)
            sdk.set_led_colors_flush_buffer()
            tdiff = timeStep - (time.time_ns() - t) / 1000000000
            if tdiff > 0:
                time.sleep(tdiff)
            else:
                accTDiff -= tdiff
        count += 1

if __name__ == "__main__":
    main()