# -*- coding: utf-8 -*-

import gettext
import sys
import webbrowser
from os.path import join, dirname

import kivy
kivy.require('1.10.0')  # noqa:E402

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import (BoundedNumericProperty, ObjectProperty, StringProperty)
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar


TIMER_OPTIONS = {
    '1/60 sec': 1 / 60.0,
    '1/30 sec': 1 / 30.0,
    '1/15 sec': 1 / 15.0,
}


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


class TransitionProgress(ProgressBar):
    """ProgressBar with pre-defined animations for fading in and out."""

    _in = Animation(opacity=1.0, duration=0.4)
    _out = Animation(opacity=0.0, duration=0.1)

    def fade_in(self):
        """Play the animation for changing the ProgressBar to be opaque."""
        self._in.start(self)

    def fade_out(self):
        """Play the animation to hide the ProgressBar."""
        self._out.start(self)


class MIDISceneManagerApp(App):
    """Simple Slideshow App with a user defined title.

    Attributes:
      title (str): Window title of the application

      timer (:class:`kivy.properties.BoundedNumericProperty`):
        Helper for the slide transition of `carousel`

      carousel (:class:`kivy.uix.carousel.Carousel`):
        Widget that holds several slides about the app
    """

    title = 'MIDISceneManager'

    language = StringProperty('en')
    translation = ObjectProperty(None, allownone=True)

    timer = BoundedNumericProperty(0, min=0, max=400)
    carousel = ObjectProperty(Carousel)

    def __init__(self, language, **kwargs):
        self.language = language
        self.switch_lang(self.language)
        super(MIDISceneManagerApp, self).__init__(**kwargs)

    def start_timer(self, *args, **kwargs):
        """Schedule the timer update routine and fade in the progress bar."""
        Logger.debug("Starting timer")
        Clock.schedule_interval(self._update_timer, self.timer_interval)
        self.progress_bar.fade_in()

    def stop_timer(self, *args, **kwargs):
        """Reset the timer and unschedule the update routine."""
        Logger.debug("Stopping timer")
        Clock.unschedule(self._update_timer)
        self.progress_bar.fade_out()
        self.timer = 0

    def delay_timer(self, *args, **kwargs):
        """Stop the timer but re-schedule it based on `anim_move_duration` of
        :attr:`MIDISceneManagerApp.carousel`.
        """
        self.stop_timer()
        Clock.schedule_once(
            self.start_timer,
            self.carousel.anim_move_duration
        )

    def build(self):
        """Initialize the GUI based on the kv file and set up events.

        Returns:
          (:class:`kivy.uix.anchorlayout.AnchorLayout`): Root widget specified
            in the kv file of the app
        """
        self.language = self.config.get('user_settings', 'language')

        user_interval = self.config.get('user_settings', 'timer_interval')
        self.timer_interval = TIMER_OPTIONS[user_interval]

        self.carousel = self.root.ids.carousel
        self.progress_bar = self.root.ids.progress_bar
        self.progress_bar.max = self.property('timer').get_max(self)

        self.start_timer()
        self.carousel.bind(on_touch_down=self.stop_timer)
        self.carousel.bind(current_slide=self.delay_timer)
        return self.root

    def build_config(self, config):
        """Create a config file on disk and assign the ConfigParser object to
        `self.config`.
        """
        config.setdefaults(
            'user_settings', {
                'timer_interval': '1/60 sec',
                'language': 'en'
            }
        )

    def build_settings(self, settings):
        """Read the user settings and create a panel from it."""
        settings_file = join(dirname(__file__), 'user_settings.json')
        settings.add_json_panel(self.title, self.config, settings_file)

    def on_config_change(self, config, section, key, value):
        """Called when the user changes the config values via the settings
        panel. If `timer_interval` is being changed update the instance
        variable of the same name accordingly.
        """
        if config is self.config:
            token = (section, key)
            if token == ('user_settings', 'timer_interval'):
                self.timer_interval = TIMER_OPTIONS[value]
            elif token == ('user_settings', 'language'):
                self.language = value

    def on_pause(self):
        """Enables the user to switch to another application causing
        :class:`MIDISceneManagerApp` to wait until the user
        switches back to it eventually.
        """
        return True

    def on_resume(self):
        """Called when the app is resumed. Used to restore data that has been
        stored in :meth:`MIDISceneManagerApp.on_pause`.
        """
        pass

    def _update_timer(self, dt):
        try:
            self.timer += 1
        except ValueError:
            self.stop_timer()
            self.carousel.load_next()
            Logger.debug("Automatically loading next slide")

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
