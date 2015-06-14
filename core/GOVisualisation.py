#!/usr/bin/env python

# -*- coding: utf-8 -*-
'''
Created on Thu Feb 13 2014

@author: Nolwenn Lavielle <nolwenn.lavielle@gmail.com>
'''

try:
    from gi.repository import Gtk as gtk
    from gi.repository.GdkPixbuf import Pixbuf
except:
    print "You may install GTK module for Python"
    exit(1)
try:
    from bs4 import BeautifulSoup
except:
    print "You may install BeautifulSoup module for Python"
    exit(1)
from HTMLParser import HTMLParser
import re
try:
    import pygraphviz as pgv
except:
    print "You may install pygraphviz module for Python"
    exit(1)
import json
import os

# cachefile feature developped by Yoann Jaroz aka tyio (irc.freenode.net, #bioinfo-fr)

OBOXML_CACHEFILE = 'goterm_oboxml_cache.json'
if not os.path.exists(OBOXML_CACHEFILE):
    with open(OBOXML_CACHEFILE, 'wb') as handle:
        json.dump({}, handle)

OBOXML_CACHE = None
with open(OBOXML_CACHEFILE, 'rb') as handle:
    OBOXML_CACHE = json.load(handle)

MINI_CACHEFILE = 'goterm_mini_cache.json'
if not os.path.exists(MINI_CACHEFILE):
    with open(MINI_CACHEFILE, 'wb') as handle:
        json.dump({}, handle)

MINI_CACHE = None
with open(MINI_CACHEFILE, 'rb') as handle:
    MINI_CACHE = json.load(handle)

class Visualise():
    def __init__(self, widget, notebook, statusbar, get_obj, goid):
        self.widget = widget
        self.notebook = notebook
        self.statusbar = statusbar
        self.get_obj = get_obj
        if isinstance(goid, str):
            self.goid = [goid]
        else:
            self.goid = goid

		# a lot of print in this script, for debug
        print self.widget
        print self.notebook
        print self.statusbar
        print self.get_obj
        print self.goid
        print goid

        viz_img = self.get_obj("vizualisationimage")

        self.qg = []
        for g in self.goid:
            self.qg.append(QuickGO(g))

        # init graph:
        # - graph directed
        # - drawn from bottom to top
        # - fill the page
        graph = pgv.AGraph(directed=True, rankdir="BT")#, ratio="fill", size="12,10")
        graph.node_attr['shape'] = 'box'

        colortypes = { 'ISA': 'black',
                'REGULATES': 'gold3',
                'NEGATIVEREGULATES': 'red',
                'POSITIVEREGULATES': 'darkgreen',
                'PARTOF': 'blue',
                'HASPART': 'purple',
                'ACCURSIN': 'cyan4'}
        dicTermToGOID = {}

        childtypes, childgoids, childterms = self.get_children(self.qg)
        print "get child infos"
        for k, v in enumerate(childtypes):
            # convert goid to term name
            termname = self.get_termname(v)
            dicTermToGOID[termname] = v
            # create first node
            graph.add_node(termname, style="filled", color="gray")
            for n, t in enumerate(childtypes[v]):
                # add edge
                dicTermToGOID[childterms[v][n]] = childgoids[v][n]
                graph.add_edge(childterms[v][n], termname, color=colortypes[t])
            if len(childtypes[v]) == 0:
                graph.add_node(termname)

        parentgoids, parentreltypes, parentreltos, parentname = self.get_parent(self.qg)
        print "get parent infos"
        # add edges to graph for first level of parents
        for k, v in enumerate(parentgoids):
            for n, t in enumerate(parentgoids[v]):
                # convert goid to term name
                termname = self.get_termname(t)
                dicTermToGOID[termname] = t
                # add edge
                graph.add_edge(parentname[v], termname, color='black')
            for n, t in enumerate(parentreltypes[v]):
                ptype = re.sub(r'_', '', t)
                ptype = ptype.upper()
                # convert goid to term name
                termname = self.get_termname(parentreltos[v][n])
                dicTermToGOID[termname] = parentreltos[v][n]
                # add edge
                graph.add_edge(parentname[v], termname, color=colortypes[ptype])

        print "construct graph"
        todo = True
        for k,v in enumerate(parentgoids):
            if len(parentgoids[v]) == 0 and len(parentreltos[v]) == 0:
                todo = False

        # while there is a parent to add
        while todo:
            parents = []
            for k,v in enumerate(parentgoids):
                for goid in parentgoids[v]:
                    qg = QuickGO(goid)
                    if qg not in parents:
                        parents.append(qg)
            for k,v in enumerate(parentreltos):
                for goid in parentreltos[v]:
                    qg = QuickGO(goid)
                    if qg not in parents:
                        parents.append(qg)

            nparentgoids, nparentreltypes, nparentreltos, parentname = self.get_parent(parents)
            parentgoid, parentreltype, parentrelto = {}, {}, {}
            pgoid, preltype, prelto = [], [], []
            # remove doublon
            for k,v in enumerate(nparentgoids):
                pgoid = [ goid for goid in nparentgoids[v] if goid != v ]
                parentgoid[v] = pgoid
            for k,v in enumerate(nparentreltypes):
                preltype = [ reltype for reltype in nparentreltypes[v] if goid != v ]
                parentreltype[v] = preltype
            for k,v in enumerate(nparentreltos):
                prelto = [ relto for relto in nparentreltos[v] if goid != v ]
                parentrelto[v] = prelto

            parentgoids, parentreltypes, parentreltos = parentgoid, parentreltype, parentrelto
            # add edges to graph for each level of parents
            for k, v in enumerate(parentgoids):
                for n, t in enumerate(parentgoids[v]):
                    # convert goid to term name
                    termname = self.get_termname(t)
                    dicTermToGOID[termname] = t
                    # add edge
                    graph.add_edge(parentname[v], termname, color='black')
                for n, t in enumerate(parentreltypes[v]):
                    if t == '':
                        ptype = 'ISA'
                    ptype = re.sub(r'_', '', t)
                    ptype = ptype.upper()
                    # convert goid to term name
                    termname = self.get_termname(parentrelto[v][n])
                    dicTermToGOID[termname] = parentreltos[v][n]
                    # add edge
                    graph.add_edge(parentname[v], termname, color=colortypes[ptype])
            if len(parentgoids) == 0 and len(parentreltos) == 0:
                todo = False
            for k,v in enumerate(parentgoids):
                if len(parentgoids[v]) == 0 and len(parentreltos[v]) == 0:
                    todo = False
                if todo == False and len(parentgoids[v]) > 0:
                    todo = True


        #print dicTermToGOID
        print "reconstruct graph to include loop"
        print "nb keys:",len(dicTermToGOID)

        # get nodes
        graphnodes = [ n.encode('ascii', 'ignore') for n in graph.nodes() ]
        # for each node
        for line, node in enumerate(graphnodes):
            nodegoid = dicTermToGOID[node]
            fctypes, fcgoids, fcterms = self.get_children([QuickGO(nodegoid)])
            # for each first child
            for fline, fnode in enumerate(fcgoids[nodegoid]):
                sctypes, scgoids, scterms = self.get_children([QuickGO(fnode)])
                if 'HASPART' in sctypes[fnode]:
                    # for each second child
                    for sline, snode in enumerate(scterms[fnode]):
                        if snode in dicTermToGOID.keys():
                            # if second child match with graphnodes
                            # then first child is child of parent
                            # second child is partial parent of first child
                            print "parent:",node,nodegoid
                            print "first child:",fnode,fcterms[nodegoid][fline]
                            print "second child:",scterms[fnode][sline],dicTermToGOID[snode]
                            print "-------------------"
                            graph.add_edge(fcterms[nodegoid][fline], \
                                    node, \
                                    color=colortypes[fctypes[nodegoid][fline]])
                            graph.add_edge(scterms[fnode][sline], \
                                    fcterms[nodegoid][fline], \
                                    color=colortypes[sctypes[fnode][sline]])

        # draw the graph
        print "draw graph then show it on GUI"
        graph.layout('dot')
        graph.draw('testgraphfromui.png')
        graph.close()

        viz_pb = Pixbuf.new_from_file('testgraphfromui.png')
        print viz_pb
        viz_img.set_from_pixbuf(viz_pb)

    def get_children(self, qgobj):
        childtypes, childgoids, childterms = {}, {}, {}

        for nb, qg in enumerate(qgobj):
            types, goids, terms = [], [], []
            mini = qg.get_mini()
            child = GetChildren()
            datas = child.get_table(mini)

            for num, data in enumerate(datas):
                if num % 3 == 0:
                    types.append(data)
                if num % 3 == 1:
                    goids.append(data)
                if num % 3 == 2:
                    data = re.sub(r' $', '', data)
                    data = re.sub(r' ', '&#92;n', data)
                    terms.append(data)

            childgoids[qg.get_goid()] = goids
            childtypes[qg.get_goid()] = types
            childterms[qg.get_goid()] = terms

        return childtypes, childgoids, childterms

    def get_parent(self, qgobj):
        parentid, parentreltype, parentrelto, parentterm = {}, {}, {}, {}
        for nb,qg in enumerate(qgobj):
            oboxml = BeautifulSoup(qg.get_oboxml())

            termname = oboxml.obo.term.find('name').get_text()
            termname = termname.encode('ascii', 'ignore')
            termname = re.sub(r' ', '&#92;n', termname)
            parentterm[qg.get_goid()] = termname

            parentgoids, parentreltypes, parentreltos = [], [], []
            for isa in oboxml.obo.term.findAll('is_a'):
                parent = isa.get_text()
                parent = parent.encode('ascii', 'ignore')   # translate unicode
                parent = re.sub(r'\n| ', '', parent)        # get GOID only

                parentgoids.append(parent)

            for relation in oboxml.obo.term.findAll('relationship'):
                # type of relationship
                reltype = relation.type.get_text()
                reltype = reltype.encode('ascii', 'ignore') # translate unicode
                reltype = re.sub(r'\n| ', '', reltype)      # get type only
                parentreltypes.append(reltype)
                # GOID in relationship
                relto = relation.to.get_text()
                relto = relto.encode('ascii', 'ignore')     # translate unicode
                parentreltos.append(relto)
            parentid[qg.get_goid()] = parentgoids
            parentreltype[qg.get_goid()] = parentreltypes
            parentrelto[qg.get_goid()] = parentreltos

        return parentid, parentreltype, parentrelto, parentterm

    def get_termname(self, goid):
        pgoid = QuickGO(goid)
        oboxml = BeautifulSoup(pgoid.get_oboxml())
        termname = oboxml.obo.term.find('name').get_text()
        termname = termname.encode('ascii', 'ignore')
        # replace each space ' ' by an endline \n in ascii mode
        termname = re.sub(r' ', '&#92;n', termname)
        return termname

class QuickGO():
    def __init__(self, goid):
        from bioservices import QuickGO as qgo
        self.qgo = qgo(verbose=False)
        self.goid = goid

    def get_mini(self):
        if self.goid not in MINI_CACHE.keys():
            MINI_CACHE[self.goid] = self.qgo.Term(self.goid, frmt="mini")
            with open(MINI_CACHEFILE, 'wb') as handle:
                json.dump(MINI_CACHE, handle)
        return MINI_CACHE[self.goid]
#        return self.qgo.Term(self.goid, frmt="mini")

    def get_oboxml(self):
        if self.goid not in OBOXML_CACHE.keys():
            OBOXML_CACHE[self.goid] = self.qgo.Term(self.goid, frmt="oboxml")
            with open(OBOXML_CACHEFILE, 'wb') as handle:
	    	    json.dump(OBOXML_CACHE, handle)
        return OBOXML_CACHE[self.goid]
#        return self.qgo.Term(self.goid, frmt="oboxml")

    def get_goid(self):
        return self.goid

class GetChildren(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_td = False
        self.in_h2 = False
        self.todo = False
        self.datas = []

    def get_table(self, html):
        self.feed(html)
        return self.datas

    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.in_h2 = True
        if tag == 'td':
            self.in_td = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.in_td = False
        if tag == 'h2':
            self.in_h2 = False

    def handle_data(self, data):
        if self.in_h2:
            if data == "Children":
                self.todo = True
            if data != "Children":
                self.todo = False

        if self.todo and self.in_td:
            data = re.sub(r'\n', '', data)
            data = re.sub(r'^ ', '', data)
            if data != "":
                self.datas.append(data)

