from pathlib import Path

from phue import Bridge

from secret import hue_bridge_host

b = Bridge(
    hue_bridge_host,
    config_file_path=str(Path(__file__).parent / 'phue.json'),
)

power_switch_id = 3


def turn_power_on():
    b.set_light(power_switch_id, "on", True)


def turn_power_off():
    b.set_light(power_switch_id, "on", False)


def get_switch_status():
    return b.get_light(power_switch_id, "on")


