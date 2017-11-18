#
# settings.py
#

import importlib
import json

from kivy.properties import StringProperty
from kivy.uix.settings import SettingOptions


class SettingDynamicOptions(SettingOptions):
    """Implementation of an option list that creates the items in the possible
    options list by calling an external method, that should be defined in
    the settings class.
    """

    options_factory = StringProperty()
    """The function's name to call each time the list should be updated.

    It should return a list of strings, to be used for the options.

    """

    def _create_popup(self, instance):
        # Update the options
        mod_name, func_name = self.options_factory.rsplit(':', 1)
        try:
            mod = importlib.import_module(mod_name)
            self.options = getattr(mod, func_name)()
        except:
            self.options = []
        super()._create_popup(instance)


settings_json = json.dumps(
[
    {
        "type": "numeric",
        "title": "Button label font size",
        "desc": "Choose the font size of the button labels",
        "section": "appearance",
        "key": "font_size"
    },
    {
        "type": "dynamic_options",
        "title": "MIDI Output",
        "desc": "Select the MIDI output port",
        "section": "midi",
        "key": "port",
        "options_factory": "midiio:get_midiout_ports"
    },
])
