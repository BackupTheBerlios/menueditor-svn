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

import os
import xdg.IniFile
import xdg.BaseDirectory

version = '0.7.1'

class Configuration(xdg.IniFile.IniFile):
    defaultGroup = 'General'

    def __init__(self):
        self.content = dict()
        path = os.path.join(xdg.BaseDirectory.save_config_path('smeg'), 'config.ini')
        if os.path.isfile(path):
            self.parse(path, ['General'])
        else:
            self.addGroup(self.defaultGroup)
            self.filename = path

    def __getitem__(self, key):
        value = self.get(key)
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            return value

    def __setitem__(self, key, value):
        if value == True:
            value = 'true'
        elif value == False:
            value = 'false'
        self.set(key, value)
        self.write()
        return True
