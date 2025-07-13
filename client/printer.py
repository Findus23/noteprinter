import os
os.environ["ESCPOS_CAPABILITIES_FILE"] = "capabilities_own.json"

from PIL.Image import Image
from escpos.printer import Usb



class OwnPrinter(Usb):
    def __init__(self):
        super().__init__(0x0525, 0xa700, profile="ODP333")

    def print_note(self, im: Image):
        self.image(im, center=True)
        self.cut(mode="FULL")


class FakePrinter(OwnPrinter):

    def print_note(self, im: Image):
        print("fake printing")
