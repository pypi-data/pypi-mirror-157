"""
Responds to events in the clarisse version section of the ConductorJob attribute editor.
"""

from ciocore import data as coredata
from cioclarisse import const as k
from cioclarisse import utils
def update(obj):
    """
    Rebuilds the clarisse_version menu.

    Args:
        obj (ConductorJob): Item on which to rebuild menu.
    """

    software_att = obj.get_attribute("clarisse_version")
    if not coredata.valid():
        software_att.add_preset(k.NOT_CONNECTED,  "0")
        return

    software_data = coredata.data().get("software")
    for i, name in enumerate(software_data.supported_host_names()):
        software_att.add_preset(name.encode("utf-8"), str(i))

    last_index = software_att.get_preset_count() - 1
    applied = software_att.get_applied_preset_index()
    if applied > last_index:
        applied = 0
        software_att.set_long(applied)
    utils.ensure_valid_dropdown_index(software_att)