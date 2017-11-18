# -*- coding: utf-8 -*-

import pytest


def test_app_title(app):
    """Simply tests if the default app title meets the expectations.

    Args:
      app (:class:`MIDISceneManagerApp`): Default app instance

    Raises:
      AssertionError: If the title does not match
    """
    assert app.title == 'MIDISceneManager'


@pytest.mark.skip()
def test_carousel(app):
    """Test for the carousel widget of the app checking the slides' names.

    Args:
      app (:class:`MIDISceneManagerApp`): Default app instance

    Raises:
      AssertionError: If the names of the slides do not match the expectations
    """
    names = [slide.name for slide in app.carousel.slides]
    expected = ['hello', 'kivy', 'cookiecutterdozer', 'license', 'github']
    assert names == expected
