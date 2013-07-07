#! /usr/bin/env python

from distutils.core import setup

setup(name="monjon",
      version="0.1",
      description="Network debugger",
      author="David Arnold",
      author_email="d@0x1.org",
      url="http://www.0x1.org/monjon",
      packages=["monjon", "monjon.gui", "monjon.proxy", "monjon.robot"],
      scripts=["bin/monjon", "bin/monjon-robot"],
      )


      
