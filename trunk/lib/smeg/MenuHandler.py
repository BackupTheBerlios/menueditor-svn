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

    def loadMenus(self, depth=1, menu=None):
        if not menu:
            menu = self.editor.menu
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
                    self.depths[depth] = self.renderer.addMenu(entry, self.depths, depth, entry.Show)
                    self.loadMenus(depth, entry)
        depth -= 1

    def loadEntries(self, menu):
        entries = []
        for entry in menu.getEntries(True):
            if isinstance(entry, xdg.Menu.MenuEntry):
                if '-usercustom' not in entry.DesktopFileID:
                    if entry.Show == 'NoDisplay' or entry.Show == True:
                        entry.parent = menu
                        entries.append(entry)
        return entries

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

    def moveEntry(self, entry, oldparent, newparent):
        self.editor.moveEntry(entry, oldparent, newparent)

    def newMenu(self, parent, name, comment, icon):
        self.editor.createMenu(parent, name, comment, icon)

    def saveMenu(self, menu, name, comment, icon):
        self.editor.editMenu(menu, name, None, comment, icon)

    def newEntry(self, parent, name, comment, command, icon, term):
        self.editor.createEntry(parent, name, command, comment, icon, term)

    def saveEntry(self, entry, name, comment, command, icon, term):
        self.editor.editEntry(entry, name, None, comment, command, icon, term)
