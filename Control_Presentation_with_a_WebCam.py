import math  # math  : mathematics
import os
import sys
import time
import tkinter
import tkinter.messagebox as msgbox
from datetime import timedelta, datetime
from tkinter import *
from tkinter import filedialog
from threading import Thread

import cv2  # opencv-python : image/video control
import numpy as np  # numpy : mathematics
import pyautogui  # PyAutoGui : mouse, keyboard control
import yaml
from PIL import Image, ImageTk
from cvzone.HandTrackingModule import HandDetector  # cvzone    : use with opencv
from pdf2image import convert_from_path
from pynput.mouse import Button as But
from pynput.mouse import Controller as Con
from pynput import keyboard


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def on_press(key):
    global break_now
    key_input = '{0}'.format(key)
    print(key_input)
    if key_input == 'Key.esc':
        break_now = True


break_now = False

pyautogui_key_list = ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
                      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                      ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
                      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                      '{', '|', '}', '~',
                      'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
                      'browserback', 'browserfavorites', 'browserforward', 'browserhome',
                      'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
                      'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
                      'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute',
                      'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'final', 'fn',
                      'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
                      'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
                      'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
                      'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
                      'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
                      'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
                      'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
                      'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
                      'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
                      'command', 'option', 'optionleft', 'optionright']

mouse = Con()

pyautogui.FAILSAFE = False  # solve PyautoGui error

cap = cv2.VideoCapture(0)  # get video     # 0 : standard webcam, 1~ : other webcam
wCam = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # video width
hCam = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # video height

TimePast = time.time()  # set time initialization

screenSizeX, screenSizeY = pyautogui.size()  # screen width, height (1920, 1080)

##################################################

imgSize = 300  # set imgWight size

offset = 20  # rectangle offset
directionOffset = 30  # direction speed offset
screenOffset = 200  # mouse offset
TimeOffset = 2  # check direction interval offset

volBar = 400  # bar image initialization
volPer = 0  # percent initialization
volPerPast = 0  # percent record initialization
smallOrLarge = 0

smoothness = 5  # vol smoothness
mouseSmoothness = 2  # mouse move smoothness

directionPast = [0, 0]  # page control coordinate record initialization
directionStrPast1 = 'X'  # direction record 1 initialization
directionStrPast2 = 'X'  # direction record 2 initialization

fingerSetV = [1, 1, 0, 0, 0]  # volume
fingerSetM = [1, 1, 1, 0, 0]  # mouse
fingerSetP = [0, 0, 0, 0, 0]

isPageControl = False  # check was page control initialization
isMouseDown = False  # check was mouse button clicked
isMouseRightDown = False
isHotkeyClicked = False
isZoomControl = False

detector = HandDetector(maxHands=1)  # make class 'get hand information'

program_start = True

prepare_time = datetime.now()
prepare_offset = 2

zoom_time = datetime.now()
zoom_time_offset = 0.1

with open("reset.yaml", 'r') as reset_file0:
    reset_dic = yaml.safe_load(reset_file0)
    finger_number_list = reset_dic.keys()


###############################################

def start():
    root.withdraw()

    global program_start, volBar, cap, volPer, smallOrLarge, volPerPast, isPageControl, isMouseDown, isMouseRightDown, TimePast, directionPast, directionStrPast1, directionStrPast2, directionOffset
    global prepare_time, isHotkeyClicked, isZoomControl, zoom_time, break_now
    print("start")

    program_start = True
    break_now = False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    while True:
        success, img = cap.read()  # read video
        img = cv2.flip(img, 1)  # video reverse left and right
        imgOutput = img.copy()  # make output image
        hands, img = detector.findHands(img)  # find hands in image

        with open("continue.yaml", 'r') as continue_file:
            continue_dic = yaml.safe_load(continue_file)
            show_video = continue_dic["video"]

        for one in range(1):
            if hands:  # find hands
                hand = hands[0]  # 'hand' is hand information
                fingers = detector.fingersUp(hand)  # check up fingers
                x, y, w, h = hand['bbox']  # get information of hand size in image

                #########

                if fingers == [0, 0, 0, 0, 0]:
                    cv2.putText(imgOutput, "Prepare", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)  # put text 'V' on image
                    prepare_time = datetime.now()
                    isHotkeyClicked = False
                    isZoomControl = False

                if datetime.now() - prepare_time < timedelta(seconds=prepare_offset):
                    if fingers == fingerSetV:  # zoom in zoom out with fingers  =======================================================
                        if datetime.now() - zoom_time < timedelta(seconds=zoom_time_offset):
                            continue

                        with open("continue.yaml", 'r') as continue_file:
                            continue_dic = yaml.safe_load(continue_file)
                            zoom_continue = continue_dic["zoom"]

                        prepare_time = datetime.now()

                        x4, y4 = hand['lmList'][4][0], hand['lmList'][4][1]  # get finger coordinate
                        x8, y8 = hand['lmList'][8][0], hand['lmList'][8][1]  # get finger coordinate
                        x0, y0 = hand['lmList'][0][0], hand['lmList'][0][1]  # get finger coordinate
                        x17, y17 = hand['lmList'][17][0], hand['lmList'][17][1]  # get finger coordinate

                        cv2.putText(imgOutput, "V", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)  # put text 'V' on image

                        cv2.circle(img, (x4, y4), 10, (255, 0, 255), cv2.FILLED)  #
                        cv2.circle(img, (x8, y8), 10, (255, 0, 255), cv2.FILLED)  #
                        cv2.line(img, (x4, y4), (x8, y8), (255, 0, 255), 3)  #
                        cv2.circle(img, (x0, y0), 10, (255, 0, 255), cv2.FILLED)  #
                        cv2.circle(img, (x17, y17), 10, (255, 0, 255), cv2.FILLED)  #
                        cv2.line(img, (x0, y0), (x17, y17), (255, 0, 255), 3)  #

                        Length = math.hypot(x8 - x4, y8 - y4)  #
                        LengthStd = math.hypot(x17 - x0, y17 - y0)  #

                        vol = max(Length / LengthStd * 170 - 10, 0)  #

                        volBar = np.interp(vol, [50, 300], [400, 150])  #
                        volBar = smoothness * round(volBar / smoothness)  #

                        volPer = np.interp(vol, [50, 300], [0, 100])  #
                        volPer = smoothness * round(volPer / smoothness)  #

                        # print(volPer)

                        if 45 <= volPer <= 55:
                            isZoomControl = False

                        if not zoom_continue and isZoomControl:
                            continue

                        if volPer <= 20:
                            pyautogui.hotkey('ctrl', '-')
                            print("small")
                            isZoomControl = True

                        elif volPer >= 80:
                            pyautogui.hotkey('ctrl', '+')
                            print("large")
                            isZoomControl = True

                        isPageControl = False  #

                        if datetime.now() - zoom_time > timedelta(seconds=zoom_time_offset):
                            zoom_time = datetime.now()

                    elif fingers == fingerSetM:  # mouse control with fingers  ========================================================
                        with open("continue.yaml", 'r') as continue_file:
                            continue_dic = yaml.safe_load(continue_file)
                            mouse_continue = continue_dic["mouse"]

                        prepare_time = datetime.now()

                        cv2.putText(imgOutput, "M", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)  # put text 'M' on image
                        x3, y3 = hand['lmList'][3][0], hand['lmList'][3][1]
                        x5, y5 = hand['lmList'][5][0], hand['lmList'][5][1]
                        x8, y8 = hand['lmList'][8][0], hand['lmList'][8][1]
                        x11, y11 = hand['lmList'][11][0], hand['lmList'][11][1]
                        x0, y0 = hand['lmList'][0][0], hand['lmList'][0][1]
                        x17, y17 = hand['lmList'][17][0], hand['lmList'][17][1]
                        cx, cy = hand['lmList'][9][0], hand['lmList'][9][1]

                        mx = np.interp(cx, (screenOffset, wCam - 1.5 * screenOffset), (0, screenSizeX))
                        mx = mouseSmoothness * round(mx / mouseSmoothness)

                        my = np.interp(cy, (screenOffset, hCam - screenOffset), (0, screenSizeY))
                        my = mouseSmoothness * round(my / mouseSmoothness)

                        cv2.circle(img, (x3, y3), 7, (255, 0, 0), cv2.FILLED)
                        cv2.circle(img, (x5, y5), 7, (255, 0, 0), cv2.FILLED)
                        cv2.circle(img, (x8, y8), 7, (255, 0, 0), cv2.FILLED)
                        cv2.circle(img, (x11, y11), 7, (255, 0, 0), cv2.FILLED)

                        mouseLength = math.hypot(x11 - x8, y11 - y8)
                        mouseRightLength = math.hypot(x5 - x3, y5 - y3)
                        LengthStd = math.hypot(x17 - x0, y17 - y0)

                        vol = mouseLength / LengthStd * 100
                        volRight = mouseRightLength / LengthStd * 100

                        if vol < 40:
                            if not isMouseDown:
                                # pyautogui.mouseDown()
                                mouse.press(But.left)
                                print("MouseDown")
                                if not mouse_continue:
                                    isMouseDown = True
                            cv2.circle(img, (x11, y11), 7, (0, 255, 255), cv2.FILLED)
                        else:
                            if isMouseDown:
                                # pyautogui.mouseUp()
                                mouse.release(But.left)
                                print("MouseUp")
                                if not mouse_continue:
                                    isMouseDown = False

                        if volRight < 40:
                            if not isMouseRightDown:
                                # pyautogui.rightClick()
                                mouse.click(But.right)
                                print("rightClick")
                                if not mouse_continue:
                                    isMouseRightDown = True
                            cv2.circle(img, (x3, y3), 7, (0, 255, 255), cv2.FILLED)
                        else:
                            if not mouse_continue:
                                isMouseRightDown = False

                        # pyautogui.moveTo(mx, my)
                        mouse.position = (mx, my)

                        isPageControl = False

                    else:
                        with open("continue.yaml", 'r') as continue_file:
                            continue_dic = yaml.safe_load(continue_file)
                            command_continue = continue_dic["command"]

                        if not command_continue and isHotkeyClicked:
                            continue

                        with open("setting.yaml", 'r') as setting_file:
                            setting_dic = yaml.safe_load(setting_file)

                        for finger_number in finger_number_list:
                            if setting_dic[finger_number]['execute'] is None:
                                continue
                            elif not setting_dic[finger_number]['execute']:
                                continue
                            else:
                                if fingers == list(map(int, list(finger_number))):
                                    hotkey_list = setting_dic[finger_number]["command"]
                                    for keys in hotkey_list:
                                        pyautogui.keyDown(keys)
                                    hotkey_list.reverse()
                                    for keys in hotkey_list:
                                        pyautogui.keyUp(keys)

                                    isHotkeyClicked = True

                ############################################

                else:
                    cv2.putText(imgOutput, "page", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)  # put text 'V' on image

                    if not isPageControl:
                        TimePast = time.time() + TimeOffset / 2
                    printDir = False
                    cx, cy = hand["center"]
                    directionStr = False

                    vx = directionPast[0] - cx

                    if vx < -directionOffset:
                        directionStr = 'left'
                        printDir = True
                    elif vx > directionOffset:
                        printDir = True
                        directionStr = 'right'

                    if directionStr and printDir and (directionStr == directionStrPast1 or directionStr == directionStrPast2 or directionStrPast1 == directionStrPast2):
                        TimeNow = time.time()
                        cv2.putText(imgOutput, f'P, {directionStr}', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 3)
                        if TimeNow - TimePast > TimeOffset:
                            pyautogui.press(directionStr)
                            print(directionStr, abs(vx))
                            TimePast = TimeNow
                    else:
                        cv2.putText(imgOutput, 'P', (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 3)

                    # print(directionStr)

                    directionPast = [cx, cy]
                    directionStrPast2 = directionStrPast1
                    directionStrPast1 = directionStr

                    isPageControl = True

                ###########################################

            try:
                if show_video:
                    imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                    imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

                    imgCropShape = imgCrop.shape

                    aspectRatio = h / w

                    if aspectRatio > 1:
                        k = imgSize / h
                        wCal = math.ceil(k * w)
                        if (not isinstance(type(imgCrop), type(None))) and (not imgCropShape[0] == 0) and (not imgCropShape[1] == 0):
                            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                            # imgResizeShape = imgResize.shape
                            wGap = math.ceil((imgSize - wCal) / 2)
                            imgWhite[:, wGap:wGap + min(wCal, 300)] = imgResize

                    else:
                        k = imgSize / w
                        hCal = math.ceil(k * h)
                        if (not isinstance(type(imgCrop), type(None))) and (not imgCropShape[0] == 0) and (not imgCropShape[1] == 0):
                            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                            # imgResizeShape = imgResize.shape
                            hGap = math.ceil((imgSize - hCal) / 2)
                            try:
                                imgWhite[hGap:hGap + min(hCal, 300), :] = imgResize
                            except:
                                continue

                    #   /** 출력  */
                    # print(x, y, w, h)
                    # print(fingers)
                    # print(volBar)

                    cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (255, 0, 255), 4)
                    cv2.imshow("ImageWhite", imgWhite)
            except:
                pass

        # print(screenSizeX, screenSizeY, wCam, hCam)
        if show_video:
            cv2.rectangle(imgOutput, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(imgOutput, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(imgOutput, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)

            cv2.imshow("Image", imgOutput)

        if break_now:
            cv2.destroyAllWindows()
            root.deiconify()
            del listener
            break

        cv2.waitKey(1)


def setting():
    pw = pyautogui.password("비밀번호를 입력해주세요. \n(초기 비밀번호는 000000 입니다.)")
    print(pw)
    with open("password.yaml", 'r') as pw_file:
        pw0 = yaml.safe_load(pw_file)['password']
        print(pw0)
    if pw is None:
        return
    elif pw != pw0:
        msgbox.showwarning(title="경고", message="비밀번호가 틀렸습니다.")
        return

    print("setting")
    root.withdraw()
    setting_root.deiconify()


def go_back():
    setting_root.withdraw()
    root.deiconify()


def reset():
    print("reset")

    MsgBox = msgbox.askquestion('Reset', 'Really reset commands?', icon='error')
    if MsgBox == 'yes':
        with open("reset.yaml", 'r') as reset_file:
            rst_dic = yaml.safe_load(reset_file)

        with open("setting.yaml", 'w') as setting_file:
            yaml.safe_dump(rst_dic, setting_file)

        label_init()


def program_exit():
    print("exit")

    root.destroy()
    sys.exit()


def customizing(num):
    global pyautogui_key_list

    with open("setting.yaml", 'r') as setting_file:
        setting_dic = yaml.safe_load(setting_file)
    key_list = list(setting_dic.keys())

    print(num)
    setting_dic[key_list[num]]['execute'] = True
    command_list = setting_dic[key_list[num]]['command']
    for count in range(len(command_list)):
        if command_list[count] is None:
            command_list.pop(count)

    command_text = ""
    first = True
    for text in command_list:
        if first:
            command_text += str(text)
            first = False
        else:
            command_text += " + " + str(text)
    if not command_text:
        command_text = "None"

    while True:
        customize = pyautogui.confirm(text=command_text, title=(str(key_list[num]) + "매크로"), buttons=['매크로 편집', '매크로 초기화', '취소'])
        if customize == '취소':
            return
        elif customize == '매크로 초기화':
            MsgBox = msgbox.askquestion(title=(str(key_list[num]) + "매크로 초기화"), message=(str(key_list[num]) + "의 매크로를 초기화 하시겠습니까?"), icon='error')
            if MsgBox == 'yes':
                setting_dic[key_list[num]]['command'] = [None]
                setting_dic[key_list[num]]['execute'] = False
                with open("setting.yaml", 'w') as setting_file:
                    yaml.safe_dump(setting_dic, setting_file)
                label_init()
            return

        temp_text = pyautogui.prompt(text="매크로를 입력해주세요", title=(str(key_list[num]) + "매크로 편집"), default=command_text)
        if temp_text is None:
            continue
        break

    temp_list = temp_text.split()
    for count in range(len(temp_list) - 1, -1, -1):
        if temp_list[count] == '+':
            temp_list.pop(count)

    for key in temp_list:
        if str(key) not in pyautogui_key_list:
            msgbox.showerror(title='key error', message='키보드에 없는 키가 포함되어 있습니다.')
            return
    setting_dic[key_list[num]]['command'] = temp_list
    setting_dic[key_list[num]]['execute'] = True

    with open("setting.yaml", 'w') as setting_file:
        yaml.safe_dump(setting_dic, setting_file)

    label_init()


def label_init():
    global label_finger

    with open("setting.yaml", 'r') as setting_file:
        setting_dic = yaml.safe_load(setting_file)

        for count in range(32):
            label_text = str(list(setting_dic.keys())[count]) + " : "
            command_text = ""
            first = True
            for j in list(setting_dic.values())[count]['command']:
                if first:
                    command_text += str(j)
                    first = False
                else:
                    command_text += " + " + str(j)
            if not command_text:
                command_text = "None"

            label_finger[count].config(text=label_text + command_text, font=("Arial", 10, "bold"), fg='black')


def mouse_continuous_control(change=True):
    with open("continue.yaml", 'r') as continue_file:
        continue_dic = yaml.safe_load(continue_file)

    if not change:
        if not continue_dic['mouse']:
            btn_continuous_mouse_click.config(text="마우스 연속 클릭 :  NO")
        else:
            btn_continuous_mouse_click.config(text="마우스 연속 클릭 : YES")
        return

    if continue_dic['mouse']:
        btn_continuous_mouse_click.config(text="마우스 연속 클릭 :  NO")
    else:
        btn_continuous_mouse_click.config(text="마우스 연속 클릭 : YES")

    continue_dic['mouse'] = not continue_dic['mouse']

    with open("continue.yaml", 'w') as continue_file:
        yaml.safe_dump(continue_dic, continue_file)


def command_continuous_control(change=True):
    with open("continue.yaml", 'r') as continue_file:
        continue_dic = yaml.safe_load(continue_file)

    if not change:
        if not continue_dic['command']:
            btn_continuous_command.config(text="커맨드 연속 입력 :  NO")
        else:
            btn_continuous_command.config(text="커맨드 연속 입력 : YES")
        return

    if continue_dic['command']:
        btn_continuous_command.config(text="커맨드 연속 입력 :  NO")
    else:
        btn_continuous_command.config(text="커맨드 연속 입력 : YES")

    continue_dic['command'] = not continue_dic['command']

    with open("continue.yaml", 'w') as continue_file:
        yaml.safe_dump(continue_dic, continue_file)


def zoom_continuous_control(change=True):
    with open("continue.yaml", 'r') as continue_file:
        continue_dic = yaml.safe_load(continue_file)

    if not change:
        if not continue_dic['zoom']:
            btn_continuous_zoom.config(text="확대/축소 연속 제어 :  NO")
        else:
            btn_continuous_zoom.config(text="확대/축소 연속 제어 : YES")
        return

    if continue_dic['zoom']:
        btn_continuous_zoom.config(text="확대/축소 연속 제어 :  NO")
    else:
        btn_continuous_zoom.config(text="확대/축소 연속 제어 : YES")

    continue_dic['zoom'] = not continue_dic['zoom']

    with open("continue.yaml", 'w') as continue_file:
        yaml.safe_dump(continue_dic, continue_file)


def video_control(change=True):
    with open("continue.yaml", 'r') as continue_file:
        continue_dic = yaml.safe_load(continue_file)

    if not change:
        if not continue_dic['video']:
            btn_show_my_video.config(text="내 비디오 화면 보기 :  NO")
        else:
            btn_show_my_video.config(text="내 비디오 화면 보기 : YES")
        return

    if continue_dic['video']:
        btn_show_my_video.config(text="내 비디오 화면 보기 :  NO")
    else:
        btn_show_my_video.config(text="내 비디오 화면 보기 : YES")

    continue_dic['video'] = not continue_dic['video']

    with open("continue.yaml", 'w') as continue_file:
        yaml.safe_dump(continue_dic, continue_file)


def open_inform():
    information_root.deiconify()
    setting_root.withdraw()


def go_back2():
    setting_root.deiconify()
    information_root.withdraw()


def button_color():
    global image_count

    if image_count == 0:
        btn_left.place_forget()
    else:
        btn_left.place(x=50, y=(screenSizeY - 130))

    if image_count == len(image_list) - 1:
        btn_right.place_forget()
    else:
        btn_right.place(x=150, y=(screenSizeY - 130))


def left():
    global image_count, image_list

    image_count = max(0, image_count - 1)
    button_color()
    canvas.create_image(0, 0, image=image_list[image_count], anchor=NW)


def right():
    global image_count, image_list

    image_count = min(len(image_list) - 1, image_count + 1)
    button_color()
    canvas.create_image(0, 0, image=image_list[image_count], anchor=NW)


def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def update_inform_(pdf_dir):
    global image_count, image_list

    for inform_file in os.scandir("inform/"):
        os.remove(inform_file.path)
        print(f"remove {inform_file.path} file")

    pages = convert_from_path(pdf_dir)

    for count, page in enumerate(pages):
        page.save("inform/" + str(count) + ".png", "PNG")

    image_count = 0
    btn_left.place_forget()
    btn_right.place(x=150, y=(screenSizeY - 130))

    image_list = []
    for file_ in os.listdir("inform/"):
        image_ = Image.open('inform/' + file_)
        width_ = screenSizeX - 30
        image_ = image_.resize((width_, int(width_ * 1.414)), Image.Resampling.LANCZOS)
        image_list.append(ImageTk.PhotoImage(image_))

    if not len(image_list) == 0:
        canvas.create_image(0, 0, image=image_list[image_count], anchor=NW)


def update_inform():
    pw = pyautogui.password("설계도 변경을 위한 비밀번호를 입력해주세요. \n(설명서를 변경하면 이전 설명서로 되돌릴 수 없습니다.)")
    print(pw)
    with open("password.yaml", 'r') as pw_file:
        pw0 = yaml.safe_load(pw_file)['password']
        print(pw0)
    if pw is None:
        return
    elif pw != pw0:
        msgbox.showwarning(title="경고", message="비밀번호가 틀렸습니다.")
        return

    pdf_dir = filedialog.askopenfilename(initialdir='', title="파일 선택", filetypes=(('pdf files', '*.pdf'), ('all files', "*'*")))

    if pdf_dir == "":
        return

    th1 = Thread(target=update_inform_, args=(pdf_dir,))
    th1.start()

    msgbox.showinfo(title="안내", message="새 설명서가 반영되는 데 몇 분의 시간이 소요될 수 있습니다.")

    th1.join()


def change_password():
    pw = pyautogui.password("기존 비밀번호를 입력해주세요. (초기 비밀번호는 000000 입니다.")
    print(pw)
    with open("password.yaml", 'r') as pw_file:
        pw0 = yaml.safe_load(pw_file)
        print(pw0['password'])
    if pw is None:
        return
    elif pw != pw0['password']:
        msgbox.showwarning(title="경고", message="비밀번호가 틀렸습니다.")
        return

    pw = pyautogui.password("변경할 비밀번호를 입력해주세요.")
    pw0['password'] = pw

    with open("password.yaml", 'w') as pw_file:
        yaml.safe_dump(pw0, pw_file)
    msgbox.showinfo(title="안내", message=f"비밀번호가 '{pw}'로 변경되었습니다.")


###########################################

if not os.path.exists("inform"):
    os.makedirs("inform")

root = Tk()
root.title("Dynamic Hand Control System")
root.geometry("500x170")
root.resizable(False, False)

# wall = PhotoImage(file="wall.png")
# wall_label = Label(image=wall)
# wall_label.place(x=-2, y=-2)

label = tkinter.Label(root)
label.config(text='카메라를 중지하려면 ESC(Escape) 키를 눌러주세요', font=("Arial", 10, "bold"), fg='black')
label.pack(side='top')

btn_start = tkinter.Button(root)
btn_start.config(text="시작", font=("Arial", 30, "bold"), fg='black')
btn_start.config(command=start)
btn_start.place(x=50, y=50)

btn_setting = tkinter.Button(root)
btn_setting.config(text="설정", font=("Arial", 30, "bold"), fg='black')
btn_setting.config(command=setting)
btn_setting.place(x=200, y=50)

btn_exit = tkinter.Button(root)
btn_exit.config(text="종료", font=("Arial", 30, "bold"), fg='black')
btn_exit.config(command=program_exit)
btn_exit.place(x=350, y=50)

btn_start.config(background='white')
btn_setting.config(background='white')
btn_exit.config(background='white')

###################################################

setting_root = Toplevel(root)
setting_root.title("Setting")
setting_root.geometry(str(screenSizeX) + 'x' + str(screenSizeY))
setting_root.resizable(False, False)
setting_root.attributes("-fullscreen", not root.attributes("-fullscreen"))  # 전체 화면

btn_go_back = tkinter.Button(setting_root)
btn_go_back.config(text="돌아가기", font=("Arial", 30, "bold"), fg='black', background='white')
btn_go_back.config(command=go_back)
btn_go_back.place(x=(screenSizeX - 240), y=(screenSizeY - 130))

btn_information = tkinter.Button(setting_root)
btn_information.config(text="사용방법", font=("Arial", 30, "bold"), fg='black', background='white')
btn_information.config(command=open_inform)
btn_information.place(x=350, y=(screenSizeY - 130))

btn_reset = tkinter.Button(setting_root)
btn_reset.config(text="커스텀 초기화", font=("Arial", 30, "bold"), fg='black', background='white')
btn_reset.config(command=reset)
btn_reset.place(x=50, y=(screenSizeY - 130))

btn_finger = []
for i in range(32):
    if i == 0 or i == 24 or i == 28:
        btn_finger.append(None)
        continue
    btn_finger.append(tkinter.Button(setting_root))
    btn_finger[i].config(text="재설정", font=("Arial", 10, "bold"), fg='black', background='white')
    if i < 16:
        btn_finger[i].place(x=50, y=(50 * (i + 1)))
    else:
        btn_finger[i].place(x=1010, y=(50 * (i - 15)))

label_finger = []
for i in range(32):
    label_finger.append(tkinter.Label(setting_root))
    label_finger[i].config(text="", font=("Arial", 10, "bold"), fg='black')
    if i < 16:
        label_finger[i].place(x=150, y=(50 * (i + 1) + 2))
    else:
        label_finger[i].place(x=1110, y=(50 * (i - 15) + 2))
label_init()

label_warning = tkinter.Label(setting_root)
label_warning.config(text="* PAGE CONTROL 기능은 아무 기능도 없는(None) 동작에서 실행되므로, PAGE CONTROL 기능을 사용하려면 모든 동작에 매크로를 설정하면 안됩니다.", font=("Arial", 12, "bold"), fg='black')
label_warning.place(x=50, y=902)

# btn_finger[0].config(command=lambda: customizing(0))
btn_finger[1].config(command=lambda: customizing(1))
btn_finger[2].config(command=lambda: customizing(2))
btn_finger[3].config(command=lambda: customizing(3))
btn_finger[4].config(command=lambda: customizing(4))
btn_finger[5].config(command=lambda: customizing(5))
btn_finger[6].config(command=lambda: customizing(6))
btn_finger[7].config(command=lambda: customizing(7))
btn_finger[8].config(command=lambda: customizing(8))
btn_finger[9].config(command=lambda: customizing(9))
btn_finger[10].config(command=lambda: customizing(10))
btn_finger[11].config(command=lambda: customizing(11))
btn_finger[12].config(command=lambda: customizing(12))
btn_finger[13].config(command=lambda: customizing(13))
btn_finger[14].config(command=lambda: customizing(14))
btn_finger[15].config(command=lambda: customizing(15))
btn_finger[16].config(command=lambda: customizing(16))
btn_finger[17].config(command=lambda: customizing(17))
btn_finger[18].config(command=lambda: customizing(18))
btn_finger[19].config(command=lambda: customizing(19))
btn_finger[20].config(command=lambda: customizing(20))
btn_finger[21].config(command=lambda: customizing(21))
btn_finger[22].config(command=lambda: customizing(22))
btn_finger[23].config(command=lambda: customizing(23))
# btn_finger[24].config(command=lambda: customizing(24))
btn_finger[25].config(command=lambda: customizing(25))
btn_finger[26].config(command=lambda: customizing(26))
btn_finger[27].config(command=lambda: customizing(27))
# btn_finger[28].config(command=lambda: customizing(28))
btn_finger[29].config(command=lambda: customizing(29))
btn_finger[30].config(command=lambda: customizing(30))
btn_finger[31].config(command=lambda: customizing(31))

btn_continuous_mouse_click = tkinter.Button(setting_root)
btn_continuous_mouse_click.config(font=("Arial", 12, "bold"), fg='black', background='white')
btn_continuous_mouse_click.config(command=lambda: mouse_continuous_control())
btn_continuous_mouse_click.place(x=1250, y=900)

btn_continuous_command = tkinter.Button(setting_root)
btn_continuous_command.config(font=("Arial", 12, "bold"), fg='black', background='white')
btn_continuous_command.config(command=lambda: command_continuous_control())
btn_continuous_command.place(x=1450, y=900)

btn_continuous_zoom = tkinter.Button(setting_root)
btn_continuous_zoom.config(font=("Arial", 12, "bold"), fg='black', background='white')
btn_continuous_zoom.config(command=lambda: zoom_continuous_control())
btn_continuous_zoom.place(x=1650, y=900)

btn_show_my_video = tkinter.Button(setting_root)
btn_show_my_video.config(font=("Arial", 12, "bold"), fg='black', background='white')
btn_show_my_video.config(command=lambda: video_control())
btn_show_my_video.place(x=1650, y=850)

mouse_continuous_control(change=False)
command_continuous_control(change=False)
zoom_continuous_control(change=False)
video_control(change=False)

##################################################

image_list = []
for file in os.listdir("inform/"):
    image = Image.open('inform/' + file)
    width = screenSizeX - 30
    image = image.resize((width, int(width * 1.414)), Image.Resampling.LANCZOS)
    image_list.append(ImageTk.PhotoImage(image))

information_root = Toplevel(root)
information_root.title("information page")
information_root.geometry(str(screenSizeX) + 'x' + str(screenSizeY))
information_root.resizable(False, False)
information_root.attributes("-fullscreen", not root.attributes("-fullscreen"))  # 전체 화면

btn_go_back2 = tkinter.Button(information_root)
btn_go_back2.config(text="돌아가기", font=("Arial", 30, "bold"), fg='black', background='white')
btn_go_back2.config(command=go_back2)
btn_go_back2.place(x=(screenSizeX - 240), y=(screenSizeY - 130))

btn_left = tkinter.Button(information_root)
btn_left.config(text="◀", font=("Arial", 30, "bold"), fg='black', background='white')
btn_left.config(command=lambda: left())
btn_left.place(x=50, y=(screenSizeY - 130))
btn_left.place_forget()

btn_right = tkinter.Button(information_root)
btn_right.config(text="▶", font=("Arial", 30, "bold"), fg='black', background='white')
btn_right.config(command=lambda: right())
btn_right.place(x=150, y=(screenSizeY - 130))

image_count = 0

canvas = tkinter.Canvas(information_root, width=screenSizeX - 25, height=screenSizeY - 150)
canvas.grid(row=0, column=0)
if not len(image_list) == 0:
    canvas.create_image(0, 0, image=image_list[image_count], anchor=NW)

y_scroll = tkinter.Scrollbar(information_root, orient='vertical', command=canvas.yview)
y_scroll.grid(row=0, column=1, sticky='ns')

canvas.config(yscrollcommand=y_scroll.set)
canvas.config(scrollregion=canvas.bbox('all'))
canvas.bind_all("<MouseWheel>", _on_mousewheel)

btn_update_inform = tkinter.Button(information_root)
btn_update_inform.config(text="설명서 변경", font=("Arial", 30, "bold"), fg='black', background='white')
btn_update_inform.config(command=update_inform)
btn_update_inform.place(x=250, y=(screenSizeY - 130))

btn_password = tkinter.Button(information_root)
btn_password.config(text="비밀번호 변경", font=("Arial", 30, "bold"), fg='black', background='white')
btn_password.config(command=change_password)
btn_password.place(x=520, y=(screenSizeY - 130))

###################################################

setting_root.withdraw()
information_root.withdraw()
root.mainloop()
