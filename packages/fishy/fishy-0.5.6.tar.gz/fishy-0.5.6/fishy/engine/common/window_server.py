import logging
import math
import traceback
from enum import Enum
from threading import Thread

import cv2
import d3dshot
import pywintypes
import win32api
import win32gui
from ctypes import windll

from fishy.helper.config import config


class Status(Enum):
    CRASHED = -1
    STOPPED = 0
    RUNNING = 1


class WindowServer:
    """
    Records the game window, and allows to create instance to process it
    """
    Screen = None
    windowOffset = None
    hwnd = None
    status = Status.STOPPED
    d3: d3dshot.D3DShot = None
    monitor_top_left = None


def init():
    """
    Executed once before the main loop,
    Finds the game window, and calculates the offset to remove the title bar
    """
    try:
        WindowServer.hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")

        monitor_id = windll.user32.MonitorFromWindow(WindowServer.hwnd, 2)
        WindowServer.monitor_top_left = win32api.GetMonitorInfo(monitor_id)["Monitor"][:2]

        rect = win32gui.GetWindowRect(WindowServer.hwnd)
        client_rect = win32gui.GetClientRect(WindowServer.hwnd)
        WindowServer.windowOffset = math.floor(((rect[2] - rect[0]) - client_rect[2]) / 2)
        WindowServer.status = Status.RUNNING

        d3 = d3dshot.create(capture_output="numpy")
        d3.display = next((m for m in d3.displays if m.hmonitor == monitor_id), None)
        WindowServer.d3 = d3

    except pywintypes.error:
        logging.error("Game window not found")
        WindowServer.status = Status.CRASHED


def loop():
    """
    Executed in the start of the main loop
    finds the game window location and captures it
    """

    temp_screen = WindowServer.d3.screenshot()

    rect = win32gui.GetWindowRect(WindowServer.hwnd)
    client_rect = win32gui.GetClientRect(WindowServer.hwnd)

    fullscreen = WindowServer.d3.display.resolution[1] == (rect[3] - rect[1])
    title_offset = ((rect[3] - rect[1]) - client_rect[3]) - WindowServer.windowOffset if not fullscreen else 0
    crop = (
        rect[0] + WindowServer.windowOffset - WindowServer.monitor_top_left[0],
        rect[1] + title_offset - WindowServer.monitor_top_left[1],
        rect[2] - WindowServer.windowOffset - WindowServer.monitor_top_left[0],
        rect[3] - WindowServer.windowOffset - WindowServer.monitor_top_left[1]
    )

    WindowServer.Screen = temp_screen[crop[1]:crop[3], crop[0]:crop[2]] if not fullscreen else temp_screen

    if WindowServer.Screen.size == 0:
        logging.error("Don't minimize or drag game window outside the screen")
        WindowServer.status = Status.CRASHED


def loop_end():
    cv2.waitKey(25)


# noinspection PyBroadException
def run():
    # todo use config
    while WindowServer.status == Status.RUNNING:
        try:
            loop()
        except Exception:
            traceback.print_exc()
            WindowServer.status = Status.CRASHED
    loop_end()


def start():
    if WindowServer.status == Status.RUNNING:
        return

    init()
    if WindowServer.status == Status.RUNNING:
        Thread(target=run).start()


def screen_ready():
    return WindowServer.Screen is not None or WindowServer.status == Status.CRASHED


def stop():
    WindowServer.status = Status.STOPPED
