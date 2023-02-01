#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import sys
from argparse import ArgumentParser
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

sys.path.append(Path(__file__).parent)
from pkm import ROOT, APPNAME  # noqa
from pkm import simpleqml, log  # noqa


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    parser = ArgumentParser(description=f'{APPNAME} - Desktop System Monitor')
    parser.add_argument('--loglevel', default='INFO', help='Set the log level (DEBUG, INFO, WARN, ERROR).')
    opts = parser.parse_args()
    if opts.loglevel:
        log.setLevel(opts.loglevel)
    # Run the app
    app = QApplication()
    desktop = simpleqml.SimpleObject(ROOT / 'sqml' / 'desktop.sqml')
    desktop.qobj.setAttribute(Qt.WA_TranslucentBackground)
    desktop.qobj.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint | Qt.CustomizeWindowHint)
    # Qt.WindowStaysOnBottomHint |
    desktop.qobj.show()
    app.exec()
