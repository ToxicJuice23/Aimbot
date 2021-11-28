import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pyautogui
import win32api, win32con, win32gui
import cv2
import math
import time
detector = hub.Module("https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1")
size_scale = 3

while True:
    hwnd = win32gui.FindWindow(None, "Krunker - Google Chrome")
    rect = win32gui.GetWindowRect(hwnd)
    region = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

    # get a screenshot
    ori_img = np.arry(pyautogui.screenshot(region=region))
    ori_img = cv2.resize(ori_img, (ori_img.shape[1] // size_scale, ori_img.shape[0] // size_scale))
    image = np.expand_dims(ori_img,0)
    img_w, img_h = image.shape[2], image.shape[1]

    #detection
    result = detector(image)
    result = {key:value.numpy() for key, value in result.items}
    boxes = result["detection_boxes"][0]
    scores = result["detection_scores"][0]
    classes = result["detection_classes"][0]

    # check every detected boxes
    detected_boxes = []
    for i, box in enumerate(boxes):
        if classes[i] == 1 and scores[1] >= 0.5:
            ymin, xmin, ymax, xmax = tuple(box)
        if ymin > 0.5 and ymax > 0.8: # csgo
        #if int(xmin * img_w * 3) < 450: # fortnite
            continue
        left, right, top, bottom = int(xmin * img_w), int(xmax * img_w), int(ymin * img_h), int(ymax * img_h)
        detected_boxes.append((left, right, top, bottom))
    
    print("Detected:", len(detected_boxes))
    # Check closest
    if len(detected_boxes) >= 1:
        min = 9999
        at = 0
        centers = []
        for i, box in enumerate(detected_boxes):
            x1, x2, y1, y2 = box
            c_x = ((x2 - x1) / 2) + x1
            c_y = ((y2 - y1) / 2) + y1
            centers.append((c_x, c_y))
            dist = math.sqrt(math.pow(img_w/2 - c_x, 2) + math.pow(img_h/2 - c_y, 2))
            if dist < min:
                min = dist
                at = i
        x = centers[at][0] - img_w/2
        y = centers[at][1] - img_h/2 - (detected_boxes[at][3] - detected_boxes[at][2]) * 0.45

        # Move mouse and shoot
        scale = 1.7 * size_scale
        x = int(x * scale)
        y = int(y * scale)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        
    time.sleep(0.1)