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

import xdg.Menu, xdg.Config, xdg.IniFile, xdg.MenuEditor
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

        self.editor = xdg.MenuEditor.MenuEditor()
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

    def save(self):
        self.editor.save()

    def parse(self):
        self.editor.parse()

    def quit(self):
        nodes = self.editor.doc.getElementsByTagName('Merge')
        for node in nodes:
            parent = node.parentNode
            parent.removeChild(node)
            parent.appendChild(node)
        self.save()

    def loadMenus(self, depth=1, menu=None):
        if not menu:
            menu = self.editor.menu
            menu.IsSeparator = False
            self.depths = {0: None}
            self.depths[1] = self.renderer.addMenu(menu, self.depths, depth, menu.Show)

        depth += 1
        for entry in menu.getEntries(True):
            if isinstance(entry, xdg.Menu.Menu):
                if entry.getName() != '':
                    if entry.Directory:
                        entry.Type = entry.Directory.Type
                    else:
                        entry.Type = 'System'
                    entry.IsSeparator = False
                    self.depths[depth] = self.renderer.addMenu(entry, self.depths, depth, entry.Show)
                    self.loadMenus(depth, entry)
            elif isinstance(entry, xdg.Menu.Separator):
                entry.IsSeparator = True
                self.depths[depth] = self.renderer.addMenu(entry, self.depths, depth, True)
        depth -= 1

    def loadEntries(self, menu):
        entries = []
        for entry in menu.getEntries(True):
            if isinstance(entry, xdg.Menu.MenuEntry):
                if '-usercustom' not in entry.DesktopFileID:
                    if entry.Show == 'NoDisplay' or entry.Show == True:
                        entry.Parent = menu
                        entry.IsSeparator = False
                        entries.append(entry)
            if isinstance(entry, xdg.Menu.Separator):
                entry.Parent = menu
                entry.IsSeparator = True
                if not menu == self.editor.menu:
                    entries.append(entry)
        return entries

    def moveEntry(self, entry, oldparent, newparent):
        self.editor.moveEntry(entry, oldparent, newparent)

    def moveMenu(self, menu, oldparent, newparent):
        self.editor.moveMenu(menu, oldparent, newparent)

    def moveEntryUp(self, entry):
        index = entry.Parent.Entries.index(entry)
        if index != 0:
            parent = entry.Parent
            before = entry.Parent.Entries[index - 1]
            if entry.IsSeparator:
                self.editor.moveSeparator(entry, parent, before=before)
            else:
                self.editor.moveEntry(entry, parent, parent, before=before)
            return True

    def moveMenuUp(self, menu):
        index = menu.Parent.Entries.index(menu)
        if index != 0:
            parent = menu.Parent
            before = menu.Parent.Entries[index - 1]
            if menu.IsSeparator:
                self.editor.moveSeparator(menu, parent, before=before)
            else:
                self.editor.moveMenu(menu, parent, parent, before=before)
            return True

    def moveEntryDown(self, entry):
        index = entry.Parent.Entries.index(entry)
        if index != len(entry.Parent.Entries) - 1:
            parent = entry.Parent
            after = entry.Parent.Entries[index + 1]
            if entry.IsSeparator:
                self.editor.moveSeparator(entry, parent, before=before)
            else:
                self.editor.moveEntry(entry, parent, parent, after=after)
            return True

    def moveMenuDown(self, menu):
        index = menu.Parent.Entries.index(menu)
        if index != len(menu.Parent.Entries) - 1:
            parent = menu.Parent
            after = menu.Parent.Entries[index + 1]
            if menu.IsSeparator:
                self.editor.moveSeparator(menu, parent, after=after)
            else:
                self.editor.moveMenu(menu, parent, parent, after=after)
            return True

    def toggleEntryVisible(self, entry, visible):
        if visible:
            self.editor.hideEntry(entry)
        else:
            self.editor.unhideEntry(entry)

    def toggleMenuVisible(self, menu, visible):
        if visible:
            self.editor.hideMenu(menu)
        else:
            self.editor.unhideMenu(menu)

    def revertEntry(self, entry):
        self.editor.revertEntry(entry)

    def revertMenu(self, menu):
        self.editor.revertMenu(menu)

    def newEntry(self, parent, name, comment, command, icon, term):
        if parent == 'Applications':
            parent = self.editor.menu
        self.editor.createEntry(parent, name, command, None, comment, icon, term)

    def newMenu(self, parent, name, comment, icon):
        print parent, type(parent)
        if parent == 'Applications':
            parent = self.editor.menu
        print parent, type(parent)
        self.editor.createMenu(parent, name, None, comment, icon)

    def newSeparator(self, entry):
        if entry == None or entry == self.editor.menu:
            parent = self.editor.menu
            after = parent.Entries[-1]
        else:
            parent = entry.Parent
            index = parent.Entries.index(entry)
            after = parent.Entries[index]
        self.editor.createSeparator(parent, after=after)

    def saveEntry(self, entry, name, comment, command, icon, term):
        self.editor.editEntry(entry, name, None, comment, command, icon, term)

    def saveMenu(self, menu, name, comment, icon):
        self.editor.editMenu(menu, name, None, comment, icon)

    def deleteEntry(self, entry):
        if entry.IsSeparator:
            self.editor.deleteSeparator(entry)
        else:
            self.editor.deleteEntry(entry)

    def deleteMenu(self, menu):
        if menu.IsSeparator:
            self.editor.deleteSeparator(menu)
        else:
            self.editor.deleteMenu(menu)
