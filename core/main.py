#!/usr/bin/env python

# -*- coding: utf-8 -*-
'''
Created on Wed Jan 8 2014

@author: Nolwenn Lavielle <nolwenn.lavielle@gmail.com>
'''

import sys
try:
    from gi.repository import Gtk as gtk
except:
    print "You may install GTK module for Python"
    sys.exit(1)

from comboboxlist import *
from QuickGOUI import QuickGOUI

los = list_of_services()

class BioServicesUI:
    def __init__(self):
        self.glade = gtk.Builder()
        self.glade.add_from_file("../gui/main.glade")
        get_obj = self.glade.get_object

        # get window object
        self.window = get_obj("window")

        # get menubar widget and initialize it
        self.menubar = get_obj("menubar")
        self.filemenu = get_obj("filemenu")

        # get statusbar widget and initialise it
        self.statusbar = get_obj("statusbar")
        self.st_contid = self.statusbar.get_context_id("statusbar")
        self.statusbar.push(self.st_contid, "Welcome!")

        # get services
        self.cb_services = get_obj("selectservice")
        self.los = get_obj("list_of_services")
        for s in los:
            self.los.append(s)
        self.cb_services.set_active(0)

        '''
        # initialize quickgo annot db combobox
        self.qg_a_adb = get_obj("quickgoannotdbcombobox")
        self.qg_a_adb.set_active(0)

        # initialize quickgo annot aspect combobox
        self.qg_a_aa = get_obj("quickgoannotaspectcombobox")
        self.qg_a_aa.set_active(0)

        # initialize quickgo annot source combobox
        self.qg_a_as = get_obj("quickgoannotsourcecombobox")
        self.qg_a_as.set_active(0)
        '''

        # initialize notebook
        self.notebook = get_obj("notebook")

        # connect signals
        self.glade.connect_signals(self)

        # show window object and all the widgets
        self.window.show_all()

        # hide notebook
        self.notebook.hide()

        self.qgoui = None

    # destroy the app
    def on_window_destroy(self, widget):
        gtk.main_quit()

    def on_menu_quit(self, widget):
        gtk.main_quit()

    # if service selected
    def on_gotoservice_clicked(self, widget):
        model = self.cb_services.get_model()
        active = self.cb_services.get_active()
        if active >= 0:
            service = model[active][0]
        self.statusbar.push(self.st_contid, "Go to service %s" % service)
        get_obj = self.glade.get_object
        #if service == "QuickGO":
        #    QuickGOUI(get_obj("framequickgoparam"), self.notebook, self.statusbar, get_obj)

    # if quickgolauchbutton clicked
    def on_quickgolaunchbutton_clicked(self, widget):
        get_obj = self.glade.get_object
        self.qgoui=QuickGOUI(get_obj("framequickgoparam"), self.notebook, self.statusbar, get_obj)
        print "quickgolaunchbutton clicked"

    def combobox_changed(self, widget, data=None):
        model = widget.get_model()
        active = widget.get_active()
        if active >= 0:
            service = model[active][0]
        self.statusbar.push(self.st_contid, "Service selected %s" % service)

    def on_change_page(self, widget, data=None, *kargs):
        pagenum = self.notebook.get_current_page()
        print "Change to page %d!" % pagenum

    def on_add_page(self, widget, data=None, *kargs):
        print "Add page!"

    def on_remove_page(self, widget, data=None, *kargs):
        pagenum = self.notebook.get_current_page()
        #print "Remove page %d!" % pagenum

    def on_tabtermexportbutton_clicked(self, widget):
        print "Will save Term datas!"
        self.qgoui.savetabterm()

    def on_tabannotexportbutton_clicked(self, widget):
        print "Will save Annotation datas!"

    def on_tabvizualisationexportbutton_clicked(self, widget):
        print "Will save Vizualisation image!"

if __name__ == "__main__":
    bs = BioServicesUI()
    gtk.main()

#sys.exit()
