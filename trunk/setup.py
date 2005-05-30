#!/usr/bin/env python

import os, sys

libdir = 'lib/smeg'
sys.path = [os.path.join(os.curdir, libdir)] + sys.path

from distutils.core import setup
import glob

setup(name = "Smeg",
      version = '0.7',
      description = "Simple Menu Editor for GNOME",
      author = "Travis Watkins",
      url = "http://www.realistanew.com/projects/smeg/",
      scripts = ['bin/smeg'],
      data_files = [(libdir, glob.glob(os.path.join(libdir, '*.py'))),
                    (libdir, glob.glob(os.path.join(libdir, '*.glade'))),
                    ('share/applications',['smeg.desktop']),
                    ('share/pixmaps', ['smeg.png']),
                   ],
      license = 'GNU GPL',
      platforms = 'posix',
      )
