#!/usr/bin/env python

# -*- coding: utf-8 -*-
'''
Created on Wed Jan 15 2014

@author: Nolwenn Lavielle <nolwenn.lavielle@gmail.com>
'''

import re
try:
    from gi.repository import Gtk as gtk, WebKit as wk
except:
    print "You may install GTK module for Python"
    exit(1)
import GOVisualisation as GOV
from savefile import SaveFile

class QuickGOUI():
    def __init__(self, widget, notebook, statusbar, get_obj):
        self.widget = widget
        self.notebook = notebook
        self.statusbar = statusbar
        self.get_obj = get_obj
        self.webview = wk.WebView()

        # get annotation parameters
        # GOID
        goidtextview = self.get_obj("quickgoannotgoidtextview")
        goidbuffer = goidtextview.get_buffer()
        if goidbuffer.get_char_count() == 0:
            self.goidannot = None
        else:
            startiter, enditer = goidbuffer.get_bounds()
            goidtext = goidbuffer.get_text(startiter, enditer, include_hidden_chars=True)
            self.goidannot = re.split("\n", goidtext)
        # protein
        proteinentry = self.get_obj("quickgoannotproteinentry")
        self.goprotein = proteinentry.get_text()
        if len(self.goprotein) == 0:
            self.goprotein = None
        # format
        self.goformatannot = "tsv"
        # limit
        limitentry = self.get_obj("quickgoannotlimitentry")
        self.golimit = limitentry.get_text()
        if len(self.golimit) == 0:
            self.golimit = 10000
        else: self.golimit=int(self.golimit)
        # col
        self.gocol = self.get_treeview_selection("quickgoannotcoltreeview", 0)
        if len(self.gocol) == 0:
            self.gocol = None
        else:
            self.gocol = ",".join([c for c in self.gocol])
        # database
        self.godb = self.get_combobox_selection("quickgoannotdbcombobox")
        if len(self.godb):
            self.godb = None
        # aspect
        self.goaspect = self.get_combobox_selection("quickgoannotaspectcombobox")
        if len(self.goaspect) == 0:
            self.goaspect = None
        # termuse
        termuse = self.get_obj("quickgoannottermuseentry")
        self.gotermuse = termuse.get_text()
        if len(self.gotermuse) == 0:
            self.gotermuse = None
        # evidence
        self.goevidence = self.get_treeview_selection("quickgoannotevidencetreeview", 0)
        if len(self.goevidence) == 0:
            self.goevidence = None
        # source
        self.gosource = self.get_combobox_selection("quickgoannotsourcecombobox")
        if len(self.gosource) == 0:
            self.gosource = None
        # reference
        ref = self.get_obj("quickgoannotrefentry")
        self.goref = ref.get_text()
        if len(self.goref) == 0:
            self.goref = None
        # taxon
        '''
            Columns for Taxon:
            0: Taxon Name
            1: Taxon ID
        '''
        self.gotaxonname = self.get_treeview_selection("quickgoannottaxtreeview", 0)
        self.gotaxonid = self.get_treeview_selection("quickgoannottaxtreeview", 1)
        if len(self.gotaxonid)  == 0:
            self.gotaxonname = None
            self.gotaxonid = None

        # get term parameters
        # GOID
        goidterm = self.get_obj("quickgotermgoidentry")
        self.goidterm = goidterm.get_text()
        if len(self.goidterm) == 0:
            self.goidterm = None
        # format
        self.goformatterm = "obo"

        # annotation options
        self.annotoptions = {
                            "protein": self.goprotein,
                            "limit": self.golimit,
                            "col": self.gocol,
                            "db": self.godb,
                            "aspect": self.goaspect,
                            "termUse": self.gotermuse,
                            "evidence": self.goevidence,
                            "source": self.gosource,
                            "ref": self.goref,
                            "tax": self.gotaxonid
                            }

        if self.goidterm != None:
            self.st_contid = self.statusbar.get_context_id("statusbar")
            self.statusbar.push(self.st_contid, "Set term datas for "+self.goidterm)
            self.statusbar.show()
            self.generate_term_tabterm_data()
            gtk.main_iteration()

            self.statusbar.push(self.st_contid, "Set annotation datas for "+self.goidterm)
            self.statusbar.show()
            self.generate_term_tabannotation_data()
            gtk.main_iteration()

            self.statusbar.push(self.st_contid, "Generate graph visualisation for "+self.goidterm)
            self.statusbar.show()
            GOV.Visualise(self.widget, self.notebook, self.statusbar, \
                    self.get_obj, self.goidterm)
        if self.goidannot != None:
            self.generate_annot_tabterm_datas()
            self.generate_annot_tabannotation_datas()
            GOV.Visualise(self.widget, self.notebook, self.statusbar, \
                    self.get_obj, self.goidannot)

        self.notebook.show()

    def get_combobox_selection(self, name=""):
        select = ""
        if len(name) > 0:
            combobox = self.get_obj(name)
            model = combobox.get_model()
            active = combobox.get_active()
            if active >= 0:
                select = model[active][0]
        return select

    def get_treeview_selection(self, name="", nbcol=0):
        treeview = self.get_obj(name)
        treeselect = treeview.get_selection()
        (model, pathiter) = treeselect.get_selected_rows()
        row = []
        for path in pathiter:
            tree_iter = model.get_iter(path)
            value = model.get_value(tree_iter, nbcol)
            row.append(value)
        return row

    def get_treeview_selectall(self, name="", nbcol=0):
        treeview = self.get_obj(name)
        treeselect = treeview.get_selection()
        treeselect.select_all()
        row = self.get_treeview_selection(name, nbcol)
        treeselect.unselect_all()
        return row

    def get_treeview_selectfirst(self, name="", nbcol=0):
        treeview = self.get_obj(name)
        treeselect = treeview.get_selection()
        treeselect.select_path(0)
        row = self.get_treeview_selection(name, nbcol)
        return row

    # fill tabulation 'Term' with data from Term
    def generate_term_tabterm_data(self):
        qgo = QuickGO(self.goidterm, self.goformatterm)
        tabtermviewtext = self.get_obj("termtabtextview")
        tabtermviewtext.get_buffer().set_text(qgo.get_term())

    # fill tabulation 'Term' with datas from Annotation
    def generate_annot_tabterm_datas(self):
        tabtermviewtext = self.get_obj("termtabtextview")
        tabtermviewtext.get_buffer().set_text("")
        for g in self.goidannot:
            qgo = QuickGO(g, self.goformatterm)
            tabtermviewtext.get_buffer().insert(tabtermviewtext.get_buffer(). \
                    get_end_iter(), qgo.get_term())

    # fill tabulation 'Annotation' with data from Term
    def generate_term_tabannotation_data(self):
        qgo = QuickGO(self.goidterm, self.goformatannot, datas=self.annotoptions)
        print qgo
        datas = [ d.split("\t") for d in qgo.get_annot().split("\n") if d != "" ]
        treeview = self.get_obj("tabannottreeview")
        treemodel = gtk.ListStore(*[str]* len(datas[0]))
        rendererText = gtk.CellRendererText()
        # reset treeview
        if len(treeview.get_columns()):
            [ treeview.remove_column(c) for c in treeview.get_columns()]
        # populate the treemodel
        for t,r in enumerate(datas[1:]):
            treemodel.append(r)
        treeview.set_model(treemodel)
        # create columns
        for t,r in enumerate(datas[0]):
            # specify treeview how to fill rows
            col = gtk.TreeViewColumn(r, rendererText, text=t)
            treeview.append_column(col)

    # fill tabulation 'Annotation' with datas from Annotation
    def generate_annot_tabannotation_datas(self):
        goidannot = ",".join([g for g in self.goidannot])
        qgo = QuickGO(goidannot, self.goformatannot, datas=self.annotoptions)
        datas = [ d.split("\t") for d in qgo.get_annot().split("\n") if d != "" ]
        treeview = self.get_obj("tabannottreeview")
        treemodel = gtk.ListStore(*[str]* len(datas[0])) #treeview.get_model()
        rendererText = gtk.CellRendererText()
        # reset treeview
        if len(treeview.get_columns()):
            [ treeview.remove_column(c) for c in treeview.get_columns()]
        # populate the treemodel
        for t,r in enumerate(datas[1:]):
            treemodel.append(r)
        treeview.set_model(treemodel)
        # create columns
        for t,r in enumerate(datas[0]):
            # specify treeview how to fill rows
            col = gtk.TreeViewColumn(r, rendererText, text=t)
            treeview.append_column(col)

    def savetabterm(self):
        SaveFile(self.get_obj("tabtermviewtext"))
#        from savefile import Save
#        Save()
#        print "Will save term datas!"
#        print "Ok, let's try!"

#    def on_tabannotexportbutton_clicked(self):
#        print "Will save annotation datas!"


class QuickGO():
    def __init__(self, goid, goformat, datas=None):
        from bioservices import QuickGO as qgo
        self.qgo = qgo(verbose=False)
        self.goid = goid
        self.goformat = goformat
        self.datas = datas

    def get_term(self):
        return str(self.qgo.Term(self.goid, frmt=self.goformat))

    def get_annot(self):
        dic = self.datas
        res = self.qgo.Annotation(goid=self.goid, \
                            frmt=self.goformat, \
                            protein=dic["protein"], limit=dic["limit"], \
                            col=dic["col"], db=dic["db"], \
                            aspect=dic["aspect"], termUse=dic["termUse"], \
                            evidence=dic["evidence"], source=dic["source"], \
                            ref=dic["ref"], tax=dic["tax"])
        return res

