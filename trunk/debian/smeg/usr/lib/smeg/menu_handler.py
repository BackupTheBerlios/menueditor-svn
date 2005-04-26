"""
  Smeg - Simple Menu Editor for GNOME

  Travis Watkins <alleykat@gmail.com>

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

  (C) Copyright 2005 Travis Watkins
"""

import xml.dom.minidom
import string, os, string, locale, sys
import xdg.DesktopEntry, xdg.BaseDirectory

class MenuHandler:
    cat_list = []
    menus = []

    def __init__(self):
        config_dir = xdg.BaseDirectory.save_config_path('menus')
        self.menu = os.path.join(config_dir, 'applications.menu')
        self.root_config = os.path.join(xdg.BaseDirectory.xdg_config_dirs[1], 'menus/applications.menu')
        if not os.access(self.menu, os.F_OK):
            open(self.menu, 'w').write(
"""<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN"
"http://www.freedesktop.org/standards/menu-spec/1.0/menu.dtd">
<Menu>
  <Name>Applications</Name>
  <MergeFile>""" + self.root_config + """</MergeFile>
</Menu>""")
        self.domtree = xml.dom.minidom.parse(self.menu)

    def intToCat(self, integer):
        if integer > (len(self.cat_list) - 1):
            return None
        return self.cat_list[integer][0]

    def catToInt(self, cat):
        i = 0
        while i < len(self.cat_list):
            if cat == self.cat_list[i][0]:
                return i
            i += 1
        return None

    def addMenu(self, name, directory=None, parent=None):
        menu = xml.dom.minidom.Element('Menu')
        menu_name = xml.dom.minidom.Element('Name')
        menu_text = xml.dom.minidom.Text()
        menu_text.data = name
        menu_name.appendChild(menu_text)
        menu.appendChild(menu_name)
        if directory:
            menu_directory = xml.dom.minidom.Element('Directory')
            menu_directory_text = xml.dom.minidom.Text()
            menu_directory_text.data = directory
            menu_directory.appendChild(menu_directory_text)
            menu.appendChild(menu_directory)
        if parent:
            parent = self.getMenu(parent)
            parent.appendChild(menu)
        else:
            self.domtree.childNodes[1].appendChild(menu)
        self.writeMenuFile()
        return self.getMenu(name)

    def getMenu(self, name):
        for menu in self.domtree.childNodes[1].getElementsByTagName('Menu'):
            for element in menu.childNodes:
                if element.nodeName != '#text':
                    try:
                        if element.childNodes[0].data == name:
                            menu.ownerDocument = self.domtree
                            return menu
                    except:
                        pass
        return self.addMenu(name)

    def removeMenu(self, name):
        menu = self.getMenu(name)
        deleted = xml.dom.minidom.Element('Deleted')
        menu.appendChild(deleted)
        self.writeMenuFile()

    def addEntry(self, name, category):
        menu = self.getMenu(category)
        include = xml.dom.minidom.Element('Include')
        include_name = xml.dom.minidom.Element('Filename')
        include_text = xml.dom.minidom.Text()
        include_text.data = name
        include_name.appendChild(include_text)
        include.appendChild(include_name)
        menu.appendChild(include)
        self.writeMenuFile()

    def removeEntry(self, entry, filename=None, name=None, category=None):
        if filename:
            entry.set('NoDisplay', 'true', 'Desktop Entry')
            entry.write(filename)
        else:
            menu = self.getMenu(category)
            exclude = xml.dom.minidom.Element('Exclude')
            exclude_name = xml.dom.minidom.Element('Filename')
            exclude_text = xml.dom.minidom.Text()
            exclude_text.data = name
            exclude_name.appendChild(exclude_text)
            exclude.appendChild(exclude_name)
            menu.appendChild(exclude)
            self.writeMenuFile()

    def writeMenuFile(self):
        open(self.menu, 'w').write(self.domtree.toxml().replace('<?xml version="1.0" ?>\n', ''))

    def loadMenus(self, renderer, depth=0, parent=None):
        import xdg.Menu
        if not parent:
            menu = xdg.Menu.parse()
            try:
                self.locale = str(locale.getdefaultlocale()[0])
                menu.setLocale(self.locale)
            except:
                self.locale = ''
            self.menus = []
            self.cat_list = []
        else:
            menu = parent

        depth += 1
        for entry in menu.getEntries():
            if isinstance(entry, xdg.Menu.Menu):
                temp = entry.getRules()[0].Rule.split("'")
                if temp[2].startswith(' in '):
                    category = temp[1]
                else:
                    category = 'GNOME'
                self.cat_list.append((entry.getName(), category, entry.Name))
                self.menus.append([entry, []])
                renderer.addMenu(entry, depth)
                self.loadMenus(renderer, depth, entry)
            elif isinstance(entry, xdg.Menu.MenuEntry):
                entry.DesktopEntry.display_category = self.menus[-1][0].getName()
                entry.DesktopEntry.original_category = self.cat_list[-1][2]
                entry.DesktopEntry.entry_type = 0
                if entry.DesktopEntry.content.has_key('Desktop Entry') and entry.DesktopEntry.content['Desktop Entry'].has_key('OnlyShowIn'):
                    if 'GNOME' in entry.DesktopEntry.content['Desktop Entry']['OnlyShowIn']:
                        self.menus[-1][1].append(entry.DesktopEntry)
                        renderer.addEntry(entry.DesktopEntry, depth)
                else:
                    self.menus[-1][1].append(entry.DesktopEntry)
                    renderer.addEntry(entry.DesktopEntry, depth)
        depth -= 1

    def saveDirectory(self, directory, name, comment, icon, filename):
        if directory:
            new_directory = directory
        else:
            new_directory = xdg.DesktopEntry.DesktopEntry()
            new_directory.addGroup('Desktop Entry')
            new_directory.set('Encoding', 'UTF-8', 'Desktop Entry')
            new_directory.set('Type', 'Directory', 'Desktop Entry')
        content = new_directory.content['Desktop Entry']
        if content.has_key('Name[' + self.locale + ']'):
            content['Name[' + self.locale + ']'] = name
        new_directory.set('Name', name, 'Desktop Entry')
        if content.has_key('Comment[' + self.locale + ']'):
            content['Comment[' + self.locale + ']'] = comment
        new_directory.set('Comment', comment, 'Desktop Entry')
        new_directory.set('Icon', icon, 'Desktop Entry')
        new_directory.write(filename)
        return new_directory

    def saveEntry(self, entry, name, comment, command, icon, useterm, category, filename):
        if entry:
            new_entry = entry
        else:
            new_entry = xdg.DesktopEntry.DesktopEntry()
            new_entry.addGroup('Desktop Entry')
            new_entry.set('Encoding', 'UTF-8', 'Desktop Entry')
            new_entry.set('Type', 'Application', 'Desktop Entry')
        content = new_entry.content['Desktop Entry']
        if content.has_key('Name[' + self.locale + ']'):
            content['Name[' + self.locale + ']'] = name
        new_entry.set('Name', name, 'Desktop Entry')
        if content.has_key('Comment[' + self.locale + ']'):
            content['Comment[' + self.locale + ']'] = comment
        new_entry.set('Comment', comment, 'Desktop Entry')

        new_entry.set('Exec', command, 'Desktop Entry')
        if useterm == True:
            new_entry.set('Terminal', 'true', 'Desktop Entry')
        else:
            new_entry.set('Terminal', 'false', 'Desktop Entry')
        new_entry.set('Categories', 'Application;' + category + ';', 'Desktop Entry')
        new_entry.set('Icon', icon, 'Desktop Entry')
        new_entry.write(filename)
