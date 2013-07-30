#! /usr/bin/env python

import unittest
if not hasattr(unittest, "SkipTest"):
    try:
        import unittest2 as unittest
    except:
        raise ImportError("monjon unittests need unittest2 for python2.x")


class TestProxy(unittest.TestCase):

    def testTest(self):
        pass


if __name__ == "__main__":
    unittest.main()
