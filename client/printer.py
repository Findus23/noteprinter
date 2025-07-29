import os

from usb.core import USBError

os.environ["ESCPOS_CAPABILITIES_FILE"] = "capabilities_own.json"

from PIL.Image import Image
from escpos.printer import Usb
from escpos.exceptions import DeviceNotFoundError


class OwnPrinter(Usb):
    def __init__(self):
        super().__init__(0x0525, 0xa700, profile="ODP333")

    def print_note(self, im: Image):
        self.image(im, center=True)
        self.cut(mode="FULL")

    def check_online(self):
        try:
            return self.is_online()
        except (DeviceNotFoundError, AssertionError, USBError):
            return False


class FakePrinter(OwnPrinter):

    def print_note(self, im: Image):
        print("fake printing")
