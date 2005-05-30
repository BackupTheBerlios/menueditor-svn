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

import gconf

version = '0.7'

class Configuration:
    def __init__(self, path):
        self.client = gconf.client_get_default()
        self.path = path
        if not self.client.dir_exists(self.path):
            self.client.add_dir(self.path, gconf.CLIENT_PRELOAD_RECURSIVE)

    def __getitem__(self, key):
        value = self.client.get(self.path + '/' + key)
        if (value):
            dtype = value.type
            if (dtype == gconf.VALUE_STRING):
                return value.get_string()
            elif (dtype == gconf.VALUE_FLOAT):
                return value.get_float()
            elif (dtype == gconf.VALUE_INT):
                return value.get_int()
            elif (dtype == gconf.VALUE_BOOL):
                return value.get_bool()
            else:
                raise ValueError("Invalid data type %s." % (dtype))
        else:
            return None

    def __setitem__(self, key, value):
        if (type(value) == str or type(value) == unicode):
            v = gconf.Value(gconf.VALUE_STRING)
            v.set_string(value)
        elif (type(value) == float):
            v = gconf.Value(gconf.VALUE_FLOAT)
            v.set_float(value)
        elif (type(value) == int):
            v = gconf.Value(gconf.VALUE_INT)
            v.set_int(value)
        elif (type(value) == bool):
            v = gconf.Value(gconf.VALUE_BOOL)
            v.set_bool(value)
        else:
            raise ValueError("Invalid data type %s." % (`type(value)`))

        self.client.set(self.path + '/' + key, v)
        return True
