#!/usr/bin/env python

import sys

from distutils.core import setup
from distutils.core import Command

class build_doc(Command):
  description = "build happy doc docs"

  user_options = [ ]

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    import happydoclib
    options = [ 
                '-ddoc',
                'SoyaModelling',
                'README',
              ]

    hp = happydoclib.HappyDoc(options) 
    hp.run()

setup(name = 'SoyaModelling',
      author = "dunk fordyce",
      author_email = "dunk@dunkfordyce.co.uk",
      url = "http://30bentham.homelinux.org/~dunk/python/SoyaModelling",
      packages = ["SoyaModelling"],
      cmdclass = {'build_doc' : build_doc}
      )
