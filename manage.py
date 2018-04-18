#!/usr/bin/env python
import os
import socket
import sys

if __name__ == "__main__":
    if socket.gethostname() == 'alpha':
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "panop.settings.dev_heyden")
    elif socket.gethostname() == 'qaci01':
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "panop.settings.qaci")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "panop.settings.base")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
