import struct

from spacepackets.ecss import PusTelecommand
from tmtccmd.pus.pus_8_funccmd import Subservices
from spacepackets.ecss.conf import get_default_tc_apid


def generate_action_command(
    object_id: bytes,
    action_id: int,
    app_data: bytes = bytes(),
    ssc: int = 0,
    apid: int = -1,
) -> PusTelecommand:
    if apid == -1:
        apid = get_default_tc_apid()
    data_to_pack = bytearray(object_id)
    data_to_pack += make_action_id(action_id) + app_data
    return PusTelecommand(
        service=8,
        subservice=Subservices.FUNCTIONAL_CMD,
        seq_count=ssc,
        app_data=data_to_pack,
        apid=apid,
    )


def make_action_id(action_id: int) -> bytearray:
    return bytearray(struct.pack("!I", action_id))
