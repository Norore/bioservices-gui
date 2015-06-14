#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 2015

@author: Nolwenn Lavielle <nolwenn.lavielle@gmail.com>
"""

import re
try:
    from gi.repository import Gtk as gtk, WebKit as wk
except:
    print "You may install GTK module for Python"
    exit(1)

class SaveFile:
    def __init__(self, widget):
        self.glade = gtk.Builder()
        self.glade.add_from_file("../gui/savefiledialog.glade")
        get_obj = self.glade.get_object

        # get filechooser object
        self.filechooser = get_obj("savefiledialog")

        self.filechooser.show()

    """
    # save term datas
    def on_tabtermexportbutton_clicked(self):
        glade = gtk.Builder()
        glade.add_from_file("../gui/savefiledialog.glade")
        get_obj = glade.get_object
        filechooser = get_obj("savefiledialog")
        filechooser.show()
    """

