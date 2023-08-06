#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import logging

from texsurgery.texsurgery import TexSurgery

class TestFormatSurgery(unittest.TestCase):
    """ Tests TexSurgery.code_surgery formatting"""

    def test_format_float(self):
        """ Tests formatting floating point numbers"""
        tex_source = r'''\usepackage[python3]{texsurgery}
\eval{3*5}
\eval[format=.2f]{3*5}
\eval[type=float]{3*5}
\eval[type=float,format=7.2f]{3*5}
\eval[format=<9.2%]{3*5}a
'''
        tex_out = r'''
15
15.00
15.0
  15.00
1500.00% a
'''
        ts = TexSurgery(tex_source).code_surgery()
        self.assertEqual(ts.src, tex_out)
        del ts #shutdow kernel

    def test_format_int(self):
        """ Tests formatting integer numbers"""
        tex_source = r'''\usepackage[python3]{texsurgery}
\eval{3*5}
\eval[format=4d]{3*5}
\eval[type=int]{3*5}
\eval[type=int,format=<4d]{3*5}a
\eval[format=<9.2%]{3*5}a
\eval[format=o]{3*5}
\eval[format=6b]{3*5}
\eval[format=4x]{3*5}
'''
        tex_out = r'''
15
  15
15
15  a
1500.00% a
17
  1111
   f
'''
        ts = TexSurgery(tex_source).code_surgery()
        self.assertEqual(ts.src, tex_out)
        del ts #shutdow kernel

    def test_format_str(self):
        """ Tests formatting strings"""
        tex_source = r'''\usepackage[python3]{texsurgery}
\eval{'aB'}
\eval[format=upper]{'aB'}
\eval[format=lower]{'aB'}
\eval[type=str]{3*5}
\eval[format=capitalize]{'test'}
'''
        tex_out = r'''
'aB'
'AB'
'ab'
15
'test'
'''
        ts = TexSurgery(tex_source).code_surgery()
        self.assertEqual(ts.src, tex_out)
        del ts #shutdow kernel

    def test_format_sstr(self):
        """ Tests formatting strings"""
        tex_source = r'''\usepackage[python3]{texsurgery}
\eval[type=string]{'aB'}
\eval[type=string,format=upper]{'aB'}
\eval[type=string,format=lower]{'aB'}
\eval[type=string]{3*5}
\eval[type=string,format=capitalize]{'test'}
'''
        tex_out = r'''
aB
AB
ab
15
Test
'''
        ts = TexSurgery(tex_source).code_surgery()
        self.assertEqual(ts.src, tex_out)
        del ts #shutdow kernel

    def test_format_tex(self):
        """ Tests formatting strings"""
        tex_source = r'''\usepackage[python3]{texsurgery}
\eval[type=tex]{'aB'}
\eval[type=tex]{3*5}
'''
        tex_out = r'''
aB
15
'''
        ts = TexSurgery(tex_source).code_surgery()
        self.assertEqual(ts.src, tex_out)
        del ts #shutdow kernel
