# -*- coding: utf-8 -*-

import os
import shutil

import pytest


@pytest.fixture(autouse=True)
def ignore_app_ini(request):
    settings_file = 'midiscenemanager/MIDISceneManagerApp.ini'
    backup_file = 'midiscenemanager/_MIDISceneManagerApp.ini'

    if os.path.exists(settings_file):
        app_ini_found = True
        shutil.copy(settings_file, backup_file)
        os.remove(settings_file)
    else:
        app_ini_found = False

    def restore_app_ini():
        if app_ini_found and os.path.exists(backup_file):
            shutil.copy(backup_file, settings_file)
            os.remove(backup_file)

    request.addfinalizer(restore_app_ini)


@pytest.fixture(scope="session")
def app(request):
    """Create an instance of the app and initialize it.

    Returns:
      :class:`MIDISceneManagerApp`: App instance

    """
    from midiscenemanager.midiscenemanager import MIDISceneManagerApp
    app = MIDISceneManagerApp('en')
    # fails unable to get a Window
    #app.load_kv()
    app.load_config()
    # fails without Kivy file loaded
    #app.build()
    return app
