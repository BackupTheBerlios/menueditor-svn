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

import pygtk
pygtk.require('2.0')
import gtk
import xdg.DesktopEntry
import os, string, random
from xdg.BaseDirectory import xdg_data_dirs

class EntryEditor(gtk.Dialog):
    def __init__(self, gui, entry=None):
        self.gui = gui
        if not entry:
            entry = xdg.DesktopEntry.DesktopEntry()
            entry.addGroup('Desktop Entry')
            entry.set('Encoding', 'UTF-8', 'Desktop Entry')
            entry.set('Type', 'Application', 'Desktop Entry')
            gtk.Dialog.__init__(self, 'Entry Editor', gui,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        else:
            gtk.Dialog.__init__(self, 'Entry Editor', gui,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_DELETE, gtk.RESPONSE_NO,
                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.entry = entry

        self.connect('response', self.responseHandler)
        self.set_size_request(325, 260)
        self.drawEditor()
        self.show_all()

    def drawEditor(self):
        table = gtk.Table(5, 2, False)
        table.set_border_width(10)
        table.set_row_spacings(5)
        table.set_col_spacings(10)
        self.vbox.pack_start(table, expand=False)
        table.show()
        self.entries = []
        content = self.entry.content['Desktop Entry']

        name_label = gtk.Label('Name:')
        name_label.set_alignment(0, 0.5)
        table.attach(name_label, 0, 1, 0, 1, gtk.FILL)
        name_label.show()
        name_entry = gtk.Entry()
        if content.has_key('Name[' + self.gui.menu_handler.locale + ']'):
            name_entry.set_text(content['Name[' + self.gui.menu_handler.locale + ']'])
        else:
            name_entry.set_text(self.entry.getName())
        table.attach(name_entry, 1, 2, 0, 1, gtk.FILL, gtk.FILL)
        name_entry.show()
        self.entries.append(name_entry)

        comment_label = gtk.Label('Comment:')
        comment_label.set_alignment(0, 0.5)
        table.attach(comment_label, 0, 1, 1, 2, gtk.FILL)
        comment_label.show()
        comment_entry = gtk.Entry()
        if content.has_key('Comment[' + self.gui.menu_handler.locale + ']'):
            comment_entry.set_text(content['Comment[' + self.gui.menu_handler.locale + ']'])
        else:
            comment_entry.set_text(self.entry.getComment())
        table.attach(comment_entry, 1, 2, 1, 2, gtk.FILL, gtk.FILL)
        comment_entry.show()
        self.entries.append(comment_entry)

        command_label = gtk.Label('Command:')
        command_label.set_alignment(0, 0.5)
        table.attach(command_label, 0, 1, 2, 3, gtk.FILL)
        command_label.show()
        command_box = gtk.HBox()
        command_box.set_spacing(2)
        command_entry = gtk.Entry()
        command_entry.set_text(self.entry.getExec())
        command_box.add(command_entry)
        command_entry.show()
        self.entries.append(command_entry)
        command_button = gtk.Button('Browse')
        command_button.connect('clicked', self.gui.selectFile, command_entry)
        command_box.add(command_button)
        command_button.show()
        table.attach(command_box, 1, 2, 2, 3, gtk.FILL, gtk.FILL)
        command_box.show()

        icon_label = gtk.Label('Icon:')
        icon_label.set_alignment(0, 0.5)
        table.attach(icon_label, 0, 1, 3, 4, gtk.FILL)
        icon_label.show()
        icon_box = gtk.HBox()
        icon_box.set_spacing(3)
        icon_button = gtk.Button('No Icon')
        icon_button.set_size_request(64, 64)
        icon_button.connect('clicked', self.gui.selectIcon)
        try:
            image = gtk.Image()
            if '/' not in self.entry.getIcon():
                icon = self.entry.getIcon().split('.')
                image.set_from_pixbuf(self.gui.theme.load_icon(icon[0], 48, ()))
            else:
                image.set_from_file(self.entry.getIcon())
            image.show()
            icon_button.my_icon_name = self.entry.getIcon() 
            icon_button.remove(icon_button.get_child())
            icon_button.add(image)
        except:
            pass
        icon_box.pack_start(icon_button, expand=False)
        icon_button.show()
        self.entries.append(icon_button)
        term_check = gtk.CheckButton('Run in terminal')
        if self.entry.getTerminal() is True:
            term_check.set_active(1)
        icon_box.pack_start(term_check, expand=False)
        term_check.show()
        self.entries.append(term_check)
        table.attach(icon_box, 1, 2, 3, 4, gtk.FILL, gtk.FILL)
        icon_box.show()

        category_label = gtk.Label('Category:')
        category_label.set_alignment(0, 0.5)
        table.attach(category_label, 0, 1, 4, 5, gtk.FILL)
        category_label.show()
        category_choices = gtk.ListStore(str)
        for cat in self.gui.menu_handler.cat_list:
            category_choices.append([cat[0]])
        category_combo = gtk.ComboBox(category_choices)
        category_cell = gtk.CellRendererText()
        category_combo.pack_start(category_cell, True)
        category_combo.add_attribute(category_cell, 'text', 0)
        try:
            category_combo.set_active(self.gui.menu_handler.catToInt(self.entry.display_category))
        except:
            pass
        table.attach(category_combo, 1, 2, 4, 5, gtk.FILL, gtk.FILL)
        category_combo.show()
        self.entries.append(category_combo)

    def responseHandler(self, dialog, id):
        name, comment, command, icon, terminal, category = self.entries
        name = name.get_text()
        comment = comment.get_text()
        command = command.get_text()
        try:
            icon = icon.my_icon_name
        except:
            icon = ''
        terminal = terminal.get_active()
        display_category = self.gui.menu_handler.intToCat(category.get_active())

        for cat in self.gui.menu_handler.cat_list:
            if display_category == cat[0]:
                category_name = cat[2]
                category = cat[1]

        if id == gtk.RESPONSE_ACCEPT:
            if len(name.strip()) == 0:
                return
            ac_s = string.maketrans('','')
            ab_s = string.lowercase + string.uppercase + '0123456789'
            username = name.translate(ac_s,  ac_s.translate(ac_s, ab_s)).lower() + '.desktop'
            if os.environ['LOGNAME'] == 'root':
                filename = self.entry.getFileName()
                if filename == '':
                    filename = os.path.join(self.gui.root_entries, username)
            else:
                filename = self.entry.getFileName()
                temp = filename.rsplit('/', 1)
                if temp[0] != '':
                    username = temp[1]
#                    if self.entry.original_category != category_name:
#                        self.gui.menu_handler.removeEntry(self.entry, name=username, category=self.entry.original_category)
#                else:
#                    if not temp[0].startswith(self.gui.user_entries):
#                        self.gui.menu_handler.removeEntry(self.entry)
#                        self.gui.menu_handler.addEntry(username, category_name)
#                    filename = os.path.join(filename, username)
                temp2 = temp[0]
                for xdg_data_dir in xdg_data_dirs:
                    xdg_data_dir = os.path.join(xdg_data_dir, 'applications')
                    temp2 = temp2.replace(xdg_data_dir, '')
                if len(temp2) and temp2[0] == '/':
                    temp2 = temp2[1:]
                path = os.path.join(self.gui.user_entries, temp2)
                if not os.access(path, os.F_OK):
                    os.makedirs(path)
                filename = os.path.join(path, username)

            self.gui.menu_handler.saveEntry(self.entry, name, comment, command, icon, terminal, category, filename)
        elif id == gtk.RESPONSE_NO:
            if os.environ['LOGNAME'] == 'root':
                filename = self.entry.getFileName()
            else:
                name = self.entry.getFileName()
                temp = name.rsplit('/', 1)
                temp2 = temp[0]
                for xdg_data_dir in xdg_data_dirs:
                    xdg_data_dir = os.path.join(xdg_data_dir, 'applications')
                    temp2 = temp2.replace(xdg_data_dir, '')
                if len(temp2) and temp2[0] == '/':
                    temp2 = temp2[1:]
                path = os.path.join(self.gui.user_entries, temp2)
                if not os.access(path, os.F_OK):
                    os.makedirs(path)
                filename = os.path.join(path, temp[1])
            self.gui.menu_handler.removeEntry(self.entry, filename=filename)
        else:
            self.destroy()
            return
        self.gui.setupMenus()
        self.destroy()

class MenuEditor(gtk.Dialog):
    def __init__(self, gui, entry=None):
        self.gui = gui
        if not entry:
            entry = xdg.DesktopEntry.DesktopEntry()
            entry.addGroup('Desktop Entry')
            entry.set('Encoding', 'UTF-8', 'Desktop Entry')
            entry.set('Type', 'Directory', 'Desktop Entry')
            gtk.Dialog.__init__(self, 'Menu Editor', gui,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        else:
            gtk.Dialog.__init__(self, 'Menu Editor', gui,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_DELETE, gtk.RESPONSE_NO,
                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.entry = entry


        self.connect('response', self.responseHandler)
        self.set_size_request(325, 220)
        self.drawEditor()
        self.show_all()

    def drawEditor(self):
        table = gtk.Table(3, 2, False)
        table.set_border_width(10)
        table.set_row_spacings(5)
        table.set_col_spacings(10)
        self.vbox.pack_start(table, expand=False)
        table.show()
        self.entries = []
        content = self.entry.content['Desktop Entry']

        name_label = gtk.Label('Name:')
        name_label.set_alignment(0, 0.5)
        table.attach(name_label, 0, 1, 0, 1, gtk.FILL)
        name_label.show()
        name_entry = gtk.Entry()
        if content.has_key('Name[' + self.gui.menu_handler.locale + ']'):
            name_entry.set_text(content['Name[' + self.gui.menu_handler.locale + ']'])
        else:
            name_entry.set_text(self.entry.getName())
        table.attach(name_entry, 1, 2, 0, 1, gtk.FILL, gtk.FILL)
        name_entry.show()
        self.entries.append(name_entry)

        comment_label = gtk.Label('Comment:')
        comment_label.set_alignment(0, 0.5)
        table.attach(comment_label, 0, 1, 1, 2, gtk.FILL)
        comment_label.show()
        comment_entry = gtk.Entry()
        if content.has_key('Comment[' + self.gui.menu_handler.locale + ']'):
            comment_entry.set_text(content['Comment[' + self.gui.menu_handler.locale + ']'])
        else:
            comment_entry.set_text(self.entry.getComment())
        table.attach(comment_entry, 1, 2, 1, 2, gtk.FILL, gtk.FILL)
        comment_entry.show()
        self.entries.append(comment_entry)

        icon_label = gtk.Label('Icon:')
        icon_label.set_alignment(0, 0.5)
        table.attach(icon_label, 0, 1, 2, 3, gtk.FILL)
        icon_label.show()
        icon_box = gtk.HBox()
        icon_box.set_spacing(3)
        icon_button = gtk.Button('No Icon')
        icon_button.set_size_request(64, 64)
        icon_button.connect('clicked', self.gui.selectIcon)
        try:
            image = gtk.Image()
            if '/' not in self.entry.getIcon():
                icon = self.entry.getIcon().split('.')
                image.set_from_pixbuf(self.gui.theme.load_icon(icon[0], 48, ()))
            else:
                image.set_from_file(self.entry.getIcon())
            image.show()
            icon_button.my_icon_name = self.entry.getIcon() 
            icon_button.remove(icon_button.get_child())
            icon_button.add(image)
        except:
            pass
        icon_box.pack_start(icon_button, expand=False)
        icon_button.show()
        self.entries.append(icon_button)
        table.attach(icon_box, 1, 2, 2, 3, gtk.FILL, gtk.FILL)
        icon_box.show()

        parent_label = gtk.Label('Parent:')
        parent_label.set_alignment(0, 0.5)
        table.attach(parent_label, 0, 1, 3, 4, gtk.FILL)
        parent_label.show()
        parent_choices = gtk.ListStore(str)
        parent_choices.append(['Applications'])
        for cat in self.gui.menu_handler.cat_list:
            parent_choices.append([cat[0]])
        parent_combo = gtk.ComboBox(parent_choices)
        parent_cell = gtk.CellRendererText()
        parent_combo.pack_start(parent_cell, True)
        parent_combo.add_attribute(parent_cell, 'text', 0)
        parent_combo.set_active(0)
        table.attach(parent_combo, 1, 2, 3, 4, gtk.FILL, gtk.FILL)
        parent_combo.show()
        self.entries.append(parent_combo)

    def responseHandler(self, dialog, id):
        name, comment, icon, parent = self.entries
        name = name.get_text()
        comment = comment.get_text()
        try:
            icon = icon.my_icon_name
        except:
            icon = ''
        parent_name = None
        if parent.get_active() != 0:
            display_parent = self.gui.menu_handler.intToCat(parent.get_active() - 1)
            for cat in self.gui.menu_handler.cat_list:
                if display_parent == cat[0]:
                    parent_name = cat[2]

        if id == gtk.RESPONSE_ACCEPT:
            new_menu = False
            if len(name.strip()) == 0:
                return
            ac_s = string.maketrans('','')
            ab_s = string.lowercase + string.uppercase + '0123456789'
            username = name.translate(ac_s,  ac_s.translate(ac_s, ab_s)).lower() + '.directory'
            if os.environ['LOGNAME'] == 'root':
                filename = self.entry.getFileName()
                if filename == '':
                    new_menu = True
                    path = self.gui.root_entries
                    filename = os.path.join(self.gui.root_directories, username)
            else:
                temp = self.entry.getFileName().rsplit('/', 1)
                if temp[0] == '':
                    new_menu = True
                    path = self.gui.user_entries
                    filename = os.path.join(self.gui.user_directories, username)
                elif temp[0] != self.gui.user_directories:
                    username = temp[1]
                    filename = os.path.join(self.gui.user_directories, username)
                else:
                    filename = os.path.join(self.gui.user_directories, temp[1])

            self.gui.menu_handler.addMenu(name, username, parent_name)
            self.gui.menu_handler.saveDirectory(self.entry, name, comment, icon, filename)
            if new_menu:
                import time
                temp = str(int(time.time())) + '.desktop'
                self.gui.menu_handler.saveEntry(None, 'Add new entry...', '', '', '', '', name, os.path.join(path, temp))
                self.gui.menu_handler.addEntry(temp, name)
            self.gui.has_new_menu = True
        elif id == gtk.RESPONSE_NO:
            name = self.entry.getFileName().rsplit('/', 1)[1]
            self.gui.menu_handler.removeMenu(name)
        else:
            self.destroy()
            return
        self.gui.setupMenus()
        self.destroy()
