#  Smeg - Simple Menu Editor for GNOME
#
#  Travis Watkins <alleykat@gmail.com>
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
#  (C) Copyright 2005 Travis Watkins

from __future__ import generators
import os, sys
cmddir = os.path.split(sys.argv[0])[0]
prefix = os.path.split(cmddir)[0]
if prefix == '': prefix = '.'
libdir = os.path.join(prefix, 'lib/smeg')
sys.path = [libdir] + sys.path

import xdg.Menu, xdg.Config, xdg.IniFile, xdg.MenuEditor, xdg.BaseDirectory
import xdg.IconTheme
import string, locale
import xml.dom.minidom, xml.dom

class MenuHandler(xdg.MenuEditor.MenuEditor):
    def __init__(self, renderer, config):
        self.config = config
        if not self.config['desktop_environment']:
            self.config['desktop_environment'] = 'GNOME'
        self.renderer = renderer
        self.setWM(self.config['desktop_environment'])
        xdg.Config.cache_time = 300
        try:
            self.locale = locale.getdefaultlocale()[0]
        except:
            self.locale = None

        xdg.MenuEditor.MenuEditor.__init__(self)
        self.editor = self
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

    def getIconPath(self, entry, size):
        if isinstance(entry, xdg.Menu.Separator):
            return None
        if isinstance(entry, (str, unicode)):
            icon = entry
        elif isinstance(entry, xdg.Menu.MenuEntry):
            icon = entry.DesktopEntry.getIcon()
        else:
            icon = entry.getIcon()
            if entry == self.editor.menu:
                return self.getIconPath('gnome-main-menu', size)
        if '/' in icon:
            if os.access(icon, os.F_OK):
                return icon
            else:
                return None

        if not 'debian' in icon or icon == 'debian-logo':
            i = 0
            while i < len(self.themes):
                path = xdg.IconTheme.getIconPath(icon, size, self.themes[i])
                if path != None:
                    return path
                i += 1
        if isinstance(entry, xdg.Menu.Menu):
            return self.getIconPath('gnome-fs-directory', size)
        elif isinstance(entry, xdg.Menu.MenuEntry):
            return self.getIconPath('application-default-icon', size)

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
            self.depths = {0: None}
            self.depths[1] = self.renderer.addMenu(menu, self.depths, depth)

        depth += 1
        for entry in menu.getEntries(True):
            if isinstance(entry, xdg.Menu.Menu):
                if entry.getName() != '':
                    if entry.Directory:
                        entry.Type = entry.Directory.Type
                    else:
                        entry.Type = 'System'
                    self.depths[depth] = self.renderer.addMenu(entry, self.depths, depth)
                    self.loadMenus(depth, entry)
        depth -= 1

    def loadEntries(self, menu):
        entries = []
        for entry in menu.getEntries(True):
            if isinstance(entry, xdg.Menu.Menu):
                if entry.getName() != '':
                    if entry.Directory:
                        entry.Type = entry.Directory.Type
                    else:
                        entry.Type = 'System'
                    yield entry
            elif isinstance(entry, xdg.Menu.MenuEntry):
                if '-usercustom' not in entry.DesktopFileID:
                    if entry.Show == 'NoDisplay' or entry.Show == True:
                        entry.Parent = menu
                        yield entry
            elif isinstance(entry, xdg.Menu.Separator):
                if self.config['desktop_environment'] == 'KDE' and entry.Show == False:
                    continue
                entry.Parent = menu
                yield entry

    def copyAppDirs(self, oldparent, newparent):
        master = self.menu.AppDirs
        new_menu = self._MenuEditor__getXmlMenu(newparent.getPath(True, True))
        for appdir in oldparent.AppDirs:
            if appdir not in master and appdir not in newparent.AppDirs:
                self._MenuEditor__addXmlTextElement(new_menu, 'AppDir', appdir)

    def copyDirectoryDirs(self, oldparent, newparent):
        master = self.menu.DirectoryDirs
        new_menu = self._MenuEditor__getXmlMenu(newparent.getPath(True, True))
        for dirdir in oldparent.DirectoryDirs:
            if dirdir not in master and dirdir not in newparent.DirectoryDirs:
                self._MenuEditor__addXmlTextElement(new_menu, 'DirectoryDir', dirdir)

    def getAccess(self, entry):
        return self.getAction(entry)

    def toggleVisible(self, entry, visible):
        if visible:
            if isinstance(entry, xdg.Menu.Menu):
                self.saveMenu(entry, nodisplay=True)
            else:
                self.saveEntry(entry, nodisplay=True)
        else:
            if isinstance(entry, xdg.Menu.Menu):
                self.saveMenu(entry, nodisplay=False)
            else:
                self.saveEntry(entry, nodisplay=False)

    def moveEntry(self, entry, oldparent, newparent, before=None, after=None, drag=False):
        if newparent.Name == 'Other':
            return False
        if oldparent == newparent and not drag:
            if after:
                if oldparent.Entries.index(entry) == len(oldparent.Entries) - 1:
                    return False
            if before:
                if oldparent.Entries.index(entry) == 0:
                    return False
        self.moveMenuEntry(entry, oldparent, newparent, after, before)
        if oldparent != newparent:
            self.copyAppDirs(oldparent, newparent)
        return True

    def moveMenu(self, menu, oldparent, newparent, before=None, after=None):
        if after:
            if oldparent.Entries.index(menu) == len(oldparent.Entries) - 1:
                return False
        if before:
            if oldparent.Entries.index(menu) == 0:
                return False
        xdg.MenuEditor.MenuEditor.moveMenu(self, menu, oldparent, newparent, after, before)
        if oldparent != newparent:
            self.copyAppDirs(oldparent, newparent)
            self.copyDirectoryDirs(oldparent, newparent)
        return True

    def moveSeparator(self, separator, parent, before=None, after=None):
        if after:
            if parent.Entries.index(separator) == len(parent.Entries) - 1:
                return False
        if before:
            if parent.Entries.index(separator) == 0:
                return False
        xdg.MenuEditor.MenuEditor.moveSeparator(self, separator, parent, after, before)
        return True

    def revertEntry(self, entry):
        self.revertMenuEntry(entry)

    def newEntry(self, parent, name, comment, command, icon, term, after):
        if name != None:
            self.createMenuEntry(parent, name, command, None, comment, icon, term, after=after)

    def newMenu(self, parent, name, comment, icon, after):
        if name != None:
            self.createMenu(parent, name, None, comment, icon, after=after)

    def newSeparator(self, parent, after):
        self.createSeparator(parent, after=after)

    def saveEntry(self, entry, name=None, comment=None, command=None, icon=None, term=None, nodisplay=None):
        self.editMenuEntry(entry, name, None, comment, command, icon, term, nodisplay=nodisplay)
        menu = self._MenuEditor__getXmlMenu(entry.Parent.getPath(True, True))
        self._MenuEditor__addXmlTextElement(menu, 'AppDir', os.path.join(xdg.BaseDirectory.xdg_data_dirs[0], 'applications'))

    def saveMenu(self, menu, name=None, comment=None, icon=None, nodisplay=None):
        xdg.MenuEditor.MenuEditor.editMenu(self, menu, name, None, comment, icon, nodisplay=nodisplay)
        menu = self._MenuEditor__getXmlMenu(menu.getPath(True, True))
        self._MenuEditor__addXmlTextElement(menu, 'DirectoryDir', os.path.join(xdg.BaseDirectory.xdg_data_dirs[0], 'desktop-directories'))

    def deleteEntry(self, entry):
        self.deleteMenuEntry(entry)
