from datetime import date, datetime, timedelta
import os
import logging
import keyring
import keyring.util.platform_ as keyring_platform
from rich.prompt import Prompt
from rich.console import Console
import tkinter as tk
from tkinter import simpledialog

# /home/username/.config/python_keyring  # Might be different for you

NAMESPACE = "canvasrobot"  # f"{__name__}"
ENTRY = "API_KEY"
URL = "URL"
start_month = 8


def get_api_data(app_window=False):
    """ ask for canvas username and api key, uses keyring to
    store them in a safe space"""

    key = keyring.get_password(NAMESPACE, ENTRY)
    if key in (None, ""):
        msg = "Enter your Canvas APi Key"
        key = simpledialog.askstring("Input",
                                     msg,
                                     parent=app_window) if app_window \
            else Prompt.ask(msg)
        keyring.set_password(NAMESPACE, ENTRY, key)

    url = keyring.get_password(NAMESPACE, URL)
    if url in (None, ""):
        msg = "Enter your Canvas URL (like https://tilburguniversity.instructure.com)"
        url = simpledialog.askstring("Input",
                                     msg,
                                     parent=app_window) if app_window \
            else Prompt.ask(msg)
        keyring.set_password(NAMESPACE, URL, url)

    return url, key


def reset_api_data(app_window=None):
    for key in (URL, ENTRY):
        keyring.delete_password(NAMESPACE, key)


ENROLLMENT_TYPES = {'student': 'StudentEnrollment',
                    'teacher': 'TeacherEnrollment',
                    'ta': 'TaEnrollment',
                    'observer': 'ObserverEnrollment',
                    'designer': 'DesignerEnrollment'}

now = datetime.now()
# July first is considered the end of season
AC_YEAR = now.year - 1 if now.month < start_month else now.year
LAST_YEAR = '-{0}-{1}'.format(AC_YEAR - 1, AC_YEAR)
THIS_YEAR = '-{0}-{1}'.format(AC_YEAR, AC_YEAR + 1)
NEXT_YEAR = '-{0}-{1}'.format(AC_YEAR + 1, AC_YEAR + 2)




