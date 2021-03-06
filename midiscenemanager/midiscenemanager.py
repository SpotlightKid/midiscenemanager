#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A simple panel for sending MIDI program change messages."""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import gettext
import webbrowser

from os.path import join, dirname

from kivy.config import Config

Config.set('kivy', 'log_level', 'debug')  # noqa:E402
#Config.set('kivy', 'log_level', 'info')

from kivy.app import App
from kivy.core.window import Window
from kivy.garden import xpopup
from kivy.logger import Logger
from kivy.modules import keybinding
from kivy.properties import BoundedNumericProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.settings import SettingsWithNoMenu
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import platform
from kivymd.card import MDCard
from kivymd.tabs import MDTab
from kivymd.theming import ThemeManager

from .config import parse_config
from .midiio import get_midiout
from .settings import SettingDynamicOptions, settings_json

from .version import __version__  # noqa:F401


def _(text):
    """This is just so we can use the default gettext format."""
    return text


class I18NLabel(Label):
    """Label that supports internationlization."""
    source_text = StringProperty('')


class RefLabel(Label):
    """Simple that opens a contained url in the webbrowser."""

    def on_ref_press(self, url):
        """Callback which is being run when the user clicks on a ref in the
        label.

        :param str url: URL to be opened in the webbrowser
        """
        Logger.info("Opening '{url}' in webbrowser.".format(url=url))
        webbrowser.open(url)


class MIDISceneManagerScreen(Screen):
    pass


# ~class MIDISceneButton(ToggleButton):
# ~    scene = StringProperty()
# ~    panel = ObjectProperty(allow_none=True)
# ~    aspect_ratio = BoundedNumericProperty(0.5, min=0.0, max=1.0)

class MIDISceneButton(ToggleButtonBehavior, MDCard):
    scene = StringProperty()
    panel = ObjectProperty(allow_none=True)
    text = StringProperty()
    subtitle = StringProperty()

    def __init__(self, text='', subtitle='', scene=None, panel=None, group='scenes'):
        super().__init__(text=text, group=group)
        self.scene = scene
        self.panel = panel


class TileGrid(GridLayout):
    pass


class ScenePanel(MDTab):
    label_size = BoundedNumericProperty(20, min=8)

    def __init__(self, name, panel):
        super().__init__(id=name, name=name, text=panel.title or name)
        #self.sv = ScrollView(size_hint=(1, None), size=(self.width, self.height))
        self.sv = ScrollView(size=(self.width, self.height))
        self.layout = TileGrid(cols=panel.cols or 5)
        if panel.rows is not None:
            self.layout.rows = panel.rows
        self.sv.add_widget(self.layout)
        self.add_widget(self.sv)


class EnhancedSettings(SettingsWithNoMenu):
    """Customized settings panel."""

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.register_type('dynamic_options', SettingDynamicOptions)


class MIDISceneManagerApp(App):
    title = 'MIDI Scene Manager'
    theme_cls = ThemeManager()
    language = StringProperty('en')
    translation = ObjectProperty(None, allownone=True)

    def __init__(self, configfile, lang='en', *args, **kwargs):
        """Class initialiser."""
        self.midi = None
        self.current_scene = None
        self.parse_config(configfile)
        self.register_event_type('on_scene_enter')
        self.register_event_type('on_scene_exit')
        self.language = lang
        self.switch_lang(self.language)
        super().__init__(*args, **kwargs)

    def parse_config(self, configfile):
        self.configfile = configfile
        for key, value in parse_config(configfile).items():
            setattr(self, key, value)

    def build(self):
        self.settings_cls = EnhancedSettings
        self.use_kivy_settings = False
        root = MIDISceneManagerScreen()

        for panelname, panel in self.panels.items():
            scene_panel = ScenePanel(panelname, panel)
            scene_panel.label_size = self.config.getint('appearance', 'font_size')

            for scenename in panel.scenes:
                scene = self.scenes.get(scenename)
                if scene:
                    button = MIDISceneButton(
                        scene=scenename,
                        group='scenes',
                        text=scene.title or "Scene: %s" % scenename,
                        panel=scene_panel
                    )
                    button.bind(on_release=self.on_scene_button)
                    scene_panel.layout.add_widget(button)

            root.ids.tp.add_widget(scene_panel)
            Logger.debug("MIDISceneManager: added scene panel '{}'.".format(panelname))
            self.panels[panelname] = scene_panel

        self.settings_panel = MDTab(id='panel_settings', name='settings', text='Settings')
        self.settings_panel.bind(on_tab_release=lambda *args: self.open_settings())
        root.ids.tp.add_widget(self.settings_panel)

        if self.default_panel and self.default_panel in self.panels:
            root.ids.tp.default_tab = self.panels[self.default_panel]

        midiport = self.config.get('midi', 'port')
        if midiport:
            self.set_midiout(midiport)

        return root

    def build_config(self, config):
        """Set the default values for the configs sections."""
        config.setdefaults('appearance', {'font_size': 20})
        config.setdefaults('midi', {'port': ""})

    def build_settings(self, settings):
        """Add our custom section to the default configuration object."""
        settings.add_json_panel('MIDISceneManager', self.config, data=settings_json)

    def display_settings(self, settings):
        """Display settings panel widget in our own TabbedPanel."""
        if not self.settings_panel.children:
            self.settings_panel.add_widget(settings)
            Logger.debug("MIDISceneManager: added content of settings panel.")
        return False

    def on_config_change(self, config, section, key, value):
        """Respond to changes in the configuration."""
        if (section, key) == ('midi', 'port'):
            self.set_midiout(value)
        elif (section, key) == ('appearance', 'font_size'):
            for panel in self.panels.values():
                try:
                    panel.label_size = int(value)
                except (TypeError, ValueError):
                    Logger.warning(
                        "MIDISceneManager: Invalid value for 'font_size': {}".format(value))

#~    def close_settings(self, settings=None):
#~        """The settings panel has been closed."""
#~        super().close_settings(settings)
#~        self.root.ids.tp.switch_to(self.root.ids.panel_scenes1)

    def on_start(self):
        self.root_window.minimum_width = 800
        self.root_window.minimum_height = 600
        self._keyboard = self.root_window.request_keyboard(self._keyboard_closed, self.root)
        self._keyboard.bind(on_key_down=self.on_key_down)

    def on_stop(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None

    def on_key_down(self, keyb, keyspec, codepoint, modifiers):
        if codepoint == 'f':
            # Toggle fullscreen mode
            keyb.window.fullscreen = not keyb.window.fullscreen
        elif keyspec[0] == 293 and modifiers == []:  # F12
            # Take screenshot of window content
            keyb.window.screenshot()
        elif keyspec[0] == 292 and modifiers == ['shift']:  # Shift + F11
            # rotate window 90 degrees
            keyb.window.rotation += 90
        elif keyspec[0] == 292 and modifiers == []:  # F11
            # Toggle landscape / portrait
            if platform in ('win', 'linux', 'macosx'):
                keyb.window.rotation = 0
                w, h = keyb.window.size
                keyb.window.size = (h, w)
                self.root_window.minimum_width, self.root_window.minimum_height = (
                    self.root_window.minimum_height, self.root_window.minimum_width)

    def on_scene_button(self, btn):
        if self.current_scene != btn.scene:
            if self.current_scene:
                self.dispatch('on_scene_exit', self.current_scene)
            self.dispatch('on_scene_enter', btn.scene)
        elif self.current_scene:
            self.dispatch('on_scene_exit', self.current_scene)
            self.current_scene = None

    def on_scene_enter(self, scene):
        Logger.debug("MIDISceneManager: entering scene '{}'.".format(scene))
        self.current_scene = scene
        if self.midi:
            for i, (cmd, args) in enumerate(self.scenes[scene].on_enter):
                try:
                    method = getattr(self.midi, 'send_' + cmd, None)
                    if method:
                        args.setdefault('delay', i)
                        method(**args)
                except Exception as exc:
                    Logger.error("Error in 'on_enter' command #{} of scene '{}': {}".format(
                                 i, scene, exc))
        Logger.debug("MIDISceneManager: current scene now: {}".format(scene))

    def on_scene_exit(self, scene):
        Logger.debug("MIDISceneManager: exiting scene '{}'".format(scene))
        if self.midi:
            for i, (cmd, args) in enumerate(self.scenes[scene].on_exit):
                try:
                    method = getattr(self.midi, 'send_' + cmd, None)
                    if method:
                        args.setdefault('delay', i)
                        method(**args)
                except Exception as exc:
                    Logger.error("Error in 'on_exit' command #{} of scene '{}': {}".format(
                                 i, scene, exc))

    def on_language(self, instance, language):
        self.switch_lang(language)

    def switch_lang(self, language):
        locale_dir = join(dirname(dirname(__file__)), 'data', 'locales')
        locales = gettext.translation(
            'midiscenemanager', locale_dir, languages=[self.language]
        )

        if sys.version_info.major >= 3:
            self.translation = locales.gettext
        else:
            self.translation = locales.ugettext

    def set_midiout(self, name):
        if not self.midi or self.midi.name != name:
            try:
                self.midi = get_midiout(name)
            except Exception as exc:
                msg = "Could not open MIDI port: {}".format(exc)
                if self.root:
                    xpopup.notification.XError(text=msg)
                else:
                    Logger.error("MIDISceneManager: " + msg)
            else:
                Logger.info("MIDISceneManager: Opened MIDI out port '{}'.".format(self.midi.name))

    def cleanup(self):
        if self.midi:
            self.midi._cleanup()


def main(args=None):
    """Main program entry point."""
    if args is None:
        args = sys.argv[1:]

    if args and len(args) > 1:
        return "Usage: midiscenemanager.py <config>"
    elif args:
        config = args[0]
    else:
        config = join(dirname(__file__), 'default.cfg')

    app = MIDISceneManagerApp(config)

    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
