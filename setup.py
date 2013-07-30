#! /usr/bin/env python

from distutils.core import setup

setup(name="monjon",
      version="1.0b1",
      description="Network debugger",
      author="David Arnold",
      author_email="d@0x1.org",
      url="http://www.0x1.org/monjon",
      packages=["monjon"],
      scripts=["scripts/monjon-robot", "scripts/monjon-cli", "scripts/monjon-proxy"],
      )


      
