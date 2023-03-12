# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import log, utils  # noqa
from pkm.qtemplate import QTemplateWidget


class ColorPicker(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/colorpicker.tmpl')

    def show(self):
        """ Show this settings window. """
        utils.centerWindow(self)
        super(ColorPicker, self).show()
