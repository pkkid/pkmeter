# -*- coding: utf-8 -*-


def get_workareas(app):
    # https://stackoverflow.com/a/52698010
    dw = app.desktop()  # dw = QDesktopWidget() also works if app is created
    taskbar_height = dw.screenGeometry().height() - dw.availableGeometry().height()
