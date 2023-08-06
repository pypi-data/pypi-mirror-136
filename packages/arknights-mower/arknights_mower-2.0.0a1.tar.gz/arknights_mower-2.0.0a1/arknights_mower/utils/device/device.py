from __future__ import annotations

from typing import Optional

from .client import Client
from .minitouch import MiniTouch
from ..log import logger, save_screenshot


class Device(object):
    """ Android Device """

    def __init__(self, device_id: str = None, connect: str = None, touch_device: str = None) -> None:
        self.device_id = device_id
        self.connect = connect
        self.touch_device = touch_device
        self.client = None
        self.minitouch = None
        self.start()

    def start(self) -> None:
        self.client = Client(self.device_id, self.connect)
        self.minitouch = MiniTouch(self.client, self.touch_device)

    def run(self, cmd: str) -> Optional[bytes]:
        return self.client.run(cmd)

    def launch(self, app: str) -> None:
        """ launch the application """
        self.run(f'am start -n {app}')

    def send_keyevent(self, keycode: int) -> None:
        """ send a key event """
        logger.debug(f'keyevent: {keycode}')
        command = f'input keyevent {keycode}'
        self.run(command)

    def send_text(self, text: str) -> None:
        """ send a text """
        logger.debug(f'text: {repr(text)}')
        text = text.replace('"', '\\"')
        command = f'input text "{text}"'
        self.run(command)

    def screencap(self, save: bool = False) -> bytes:
        """ get a screencap """
        command = 'screencap -p'
        screencap = self.run(command)
        if save:
            save_screenshot(screencap)
        return screencap

    def current_focus(self) -> str:
        """ detect current focus app """
        command = 'dumpsys window | grep mCurrentFocus'
        line = self.run(command).decode('utf8')
        return line.strip()[:-1].split(' ')[-1]

    def tap(self, point: tuple[int, int]) -> None:
        """ tap """
        logger.debug(f'tap: {point}')
        self.minitouch.tap([point])

    def swipe(self, points: list[tuple[int, int]], duration: int = 100, part: int = 10, fall: bool = True, lift: bool = True) -> None:
        """ swipe """
        logger.debug(f'swipe: {points}')
        points_num = len(points)
        duration //= points_num - 1
        self.minitouch.smooth_swipe(points, duration=duration, part=part, fall=fall, lift=lift)
