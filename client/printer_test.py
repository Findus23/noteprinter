from escpos.constants import PAPER_FULL_CUT, ESC

from printer import OwnPrinter

# p = printer.File("test")
p = OwnPrinter()
p.profile.profile_data["fonts"]["0"]["columns"] = 50
print(p.is_online())
print(p.paper_status())
# p.cut()
p.print_and_feed(5)
p.text("test\n")
# p._raw(PAPER_FULL_CUT)
print(PAPER_FULL_CUT)
print(PAPER_FULL_CUT.hex())
print()
# p._raw(b"\x1d\x56\x42\x05")
p._raw(b"\x1b\x69")
# p._raw(ESC + b"m")
p.text("bla\n")
