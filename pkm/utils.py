# -*- coding: utf-8 -*-

class Bunch(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


def get_workareas(app):
    # https://stackoverflow.com/a/52698010
    dw = app.desktop()  # dw = QDesktopWidget() also works if app is created
    taskbar_height = dw.screenGeometry().height() - dw.availableGeometry().height()
