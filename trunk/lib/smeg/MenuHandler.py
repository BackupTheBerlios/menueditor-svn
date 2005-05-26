#  Smeg - Simple Menu Editor for GNOME
#
#  Travis Watkins <alleykat@gmail.com>
#  Matt Kynaston <mattkyn@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#  (C) Copyright 2005 Travis Watkins, Matt Kynaston

import os, sys
cmddir = os.path.split(sys.argv[0])[0]
prefix = os.path.split(cmddir)[0]
if prefix == '': prefix = '.'
libdir = os.path.join(prefix, 'lib/smeg')
sys.path = [libdir] + sys.path

import xdg.Menu, xdg.Config, xdg.BaseDirectory, xdg.DesktopEntry, xdg.IniFile
import xdg.IconTheme
import string, locale
import xml.dom.minidom, xml.dom

class MenuHandler:
    def __init__(self, renderer, config):
        self.config = config
        if not self.config['desktop_environment']:
            self.config['desktop_environment'] = 'GNOME'
        self.renderer = renderer
        self.setWM(self.config['desktop_environment'])
        try:
            self.locale = locale.getdefaultlocale()[0]
        except:
            self.locale = None

        config_dir = xdg.BaseDirectory.save_config_path('menus')
        self.menu_path = os.path.join(config_dir, 'applications.menu')
        root_config = os.path.join(xdg.BaseDirectory.xdg_config_dirs[1], 'menus/applications.menu')
        if not os.access(self.menu_path, os.F_OK):
            open(self.menu_path, 'w').write(
"""<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN" "http://standards.freedesktop.org/menu-spec/menu-1.0.dtd">
<Menu>
  <Name>Applications</Name>
  <MergeFile type="parent">""" + root_config + """</MergeFile>
</Menu>""")
        self.domtree = xml.dom.minidom.parse(self.menu_path)
        self.getIconThemes()

    def setWM(self, wm):
        xdg.Config.setWindowManager(wm)

    def getIconThemes(self):
        import config
        self.themes = []
        kde_theme, gnome_theme = None, None

        gnome_theme = config.Configuration('/desktop/gnome/interface')['icon_theme']
        try:
            fd = os.popen3('kde-config --path config')
            output = fd[1].readlines()
            cfgdir, tmp = output[0].split(':', 1)
 
            config = xdg.IniFile.IniFile()
            config.parse(os.path.join(cfgdir, 'kdeglobals'), ['General'])
            theme = config.get('Theme', 'Icons')
            if theme:
                kde_theme = theme
            else:
                kde_theme = 'default.kde'
        except:
            kde_theme = 'default.kde'
        if self.config['desktop_environment'] == 'GNOME':
            self.themes = [gnome_theme, kde_theme]
        elif self.config['desktop_environment'] == 'KDE':
            self.themes = [kde_theme, gnome_theme]
        else:
            self.themes = ['hicolor',]
        if self.config['use_custom_theme']:
            self.themes = [self.config['custom_theme_name'],]

    def getIconPath(self, name, size):
        if '/' in name:
            if os.access(name, os.F_OK):
                path = name
            else:
                path = None
        else:
            i = 0
            while i < len(self.themes):
                path = xdg.IconTheme.getIconPath(name, size, self.themes[i])
                if path != None:
                    break
                i += 1
        return path

    def getName(self, name):
        ac_s = string.maketrans('', '')
        ab_s = string.lowercase + string.uppercase + '0123456789'
        return name.translate(ac_s, ac_s.translate(ac_s, ab_s)).lower()

    def appendTextElement(self, parent, name, text):
        node = self.domtree.createElement(name)
        text = self.domtree.createTextNode(text)
        node.appendChild(text)
        return parent.appendChild(node)

    def appendExcludeFileName(self, element, filename):
        exclude_node = self.domtree.createElement('Exclude')
        filename_node = self.domtree.createElement('Filename')
        text = self.domtree.createTextNode(filename)
        exclude_node.appendChild(filename_node)
        filename_node.appendChild(text)
        return element.appendChild(exclude_node)

    def appendIncludeFileName(self, element, filename):
        include_node = self.domtree.createElement('Include')
        filename_node = self.domtree.createElement('Filename')
        text = self.domtree.createTextNode(filename)
        include_node.appendChild(filename_node)
        filename_node.appendChild(text)
        return element.appendChild(include_node)

    def getLastChildNamed(self, parent, nodeName, nodeValue = False, create = False):
        children = parent.childNodes[:]
        children.reverse()
        for child in children:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.nodeName == nodeName:
                if nodeValue and child.hasChildNodes() and child.childNodes[0].nodeValue == nodeValue:
                    return child
                elif not nodeValue:
                    return child
        if create and nodeValue:
            return self.appendTextElement(parent, nodeName, nodeValue)
        elif create:
            return  parent.appendChild(self.Doc.createElement(nodeName))
        return None

    def appendMenuElement(self, parent, name):
        el = self.domtree.createElement('Menu')
        self.appendTextElement(el, 'Name', name)
        temp = parent.appendChild(el)
        self.writeMenuFile()
        return temp

    def getMenuFromPath(self, path, create=False, element=None):
        if element == None:
            element = self.domtree.documentElement

        found = None
        menus = path.split('/')
        name = menus.pop(0)
        
        if self.getLastChildNamed(element, 'Name', name):
            if len(menus):
                children = element.childNodes[:]
                children.reverse()
                for child in children:
                    if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.nodeName == 'Menu':
                        found = self.getMenuFromPath('/'.join(menus), create, child)
                        if found: break
                if not found and create:
                    child = self.appendMenuElement(element, menus[0])
                    found = self.getMenuFromPath('/'.join(menus), create, child)
            else:
                found = element
            
        return found

    def writeMenuFile(self):
        open(self.menu_path, 'w').write(self.domtree.toxml().replace('<?xml version="1.0" ?>\n', ''))

    def loadMenus(self, depth=1, menu=None):
        if not menu:
            menu = xdg.Menu.parse()
            self.depths = {0: None}
            self.depths[1] = self.renderer.addMenu(menu, self.depths, depth, menu.Show)

        depth += 1
        for entry in menu.getEntries(True):
            if isinstance(entry, xdg.Menu.Menu):
                if entry.getName() != '':
                    try:
                        entry.Type = entry.Directory.Type
                    except:
                        entry.Type = 'System'
                    self.depths[depth] = self.renderer.addMenu(entry, self.depths, depth, entry.Show)
                    self.loadMenus(depth, entry)
        depth -= 1

    def loadEntries(self, menu):
        entries = []
        for entry in menu.getEntries(True):
            if isinstance(entry, xdg.Menu.MenuEntry):
                if entry.Show == 'Hidden' or entry.Show == True:
                    entry.parent = menu
                    entries.append(entry)
        return entries

    def toggleEntryVisible(self, entry, visible):
        desktop = entry.DesktopEntry
        if visible:
            desktop.set('Hidden', 'true')
        else:
            desktop.set('Hidden', 'false')
        entry.save()

    def toggleMenuVisible(self, menu, visible):
        xmlmenu = self.getMenuFromPath(menu.getPath(True, True), True)

        if visible:
            el = self.domtree.createElement('Deleted')
        else:
            el = self.domtree.createElement('NotDeleted')
        xmlmenu.appendChild(el)
        self.writeMenuFile()

    def moveEntry(self, fileid, oldmenu, newmenu):
        oldxml = self.getMenuFromPath(oldmenu.getPath(True, True), True)
        newxml = self.getMenuFromPath(newmenu.getPath(True, True), True)
        self.appendExcludeFileName(oldxml, fileid)
        self.appendIncludeFileName(newxml, fileid)
        self.writeMenuFile()

    def newMenu(self, path, name, comment, icon):
        xmlparent = self.getMenuFromPath(path, True)
        menu = self.appendMenuElement(xmlparent, name)
        directory = self.saveMenu(None, name, comment, icon)
        el = self.appendTextElement(menu, 'Directory', directory)
        self.writeMenuFile()

    def saveMenu(self, entry, name, comment, icon):
        new_entry = False
        if not entry:
            new_entry = True
            desktop = xdg.DesktopEntry.DesktopEntry()
            desktop.addGroup('Desktop Entry')
            desktop.defaultGroup = 'Desktop Entry'
            desktop.set('Encoding', 'UTF-8')
            desktop.set('Type', 'Directory')
            directory_name = self.getName(name) + '.directory'
            desktop.new(directory_name)
        else:
            if not entry.Directory:
                self.newMenu(os.path.split(entry.getPath(True, True))[0], name, comment, icon)
                return
            desktop = entry.Directory.DesktopEntry
            directory_name = os.path.split(desktop.getFileName())[1]
        desktop.set('Name', name)
        desktop.set('Comment', comment)
        if self.locale:
            desktop.set('Name[' + str(self.locale) + ']', name)
            desktop.set('Comment[' + str(self.locale) + ']', comment)
        desktop.set('Icon', icon)
        desktop.save()
        return directory_name

    def newEntry(self, path, name, comment, command, icon, term):
        xmlparent = self.getMenuFromPath(path, True)
        entry = self.saveEntry(None, name, comment, command, icon, term)
        el = self.appendIncludeFileName(xmlparent, entry)
        self.writeMenuFile()

    def saveEntry(self, entry, name, comment, command, icon, term):
        new_entry = False
        if not entry:
            new_entry = True
            desktop = xdg.DesktopEntry.DesktopEntry()
            desktop.addGroup('Desktop Entry')
            desktop.defaultGroup = 'Desktop Entry'
            desktop.set('Encoding', 'UTF-8')
            desktop.set('Type', 'Application')
            desktop_name = self.getName(name) + '.desktop'
            desktop.new(desktop_name)
        else:
            desktop = entry.DesktopEntry
            desktop_name = entry.DesktopFileID
        desktop.set('Name', name)
        desktop.set('Comment', comment)
        if self.locale:
            desktop.set('Name[' + str(self.locale) + ']', name)
            desktop.set('Comment[' + str(self.locale) + ']', comment)
        desktop.set('Exec', command)
        desktop.set('Icon', icon)
        if term == True:
            desktop.set('Terminal', 'true')
        else:
            desktop.set('Terminal', 'false')
        if new_entry:
            desktop.save()
        else:
            entry.save()
        return desktop_name
